"""Original Brain Entity-inspired still/feedback study; run from apps/deforum.

uv run --env-file .env --with pillow python projects/brain-entity-study/experiments/render.py stills
uv run --env-file .env --with pillow python projects/brain-entity-study/experiments/render.py animate --anchor PATH
"""

import argparse
import json
from pathlib import Path
import sys

APP = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
import serverless_client

WIDTH, HEIGHT, COUNT, PACK_COLUMNS = 1024, 576, 48, 7
STYLE = ("bold science fiction comic book illustration, thick confident black ink contours, "
         "intricate engraved hatching and crisp small line details, flat cel shaded colors, "
         "deep black background, petrol teal shadows, pale cyan and ivory highlights, "
         "burnt orange accent shapes, restricted orange teal cream palette, graphic poster composition")
SUBJECTS = [
    "a colossal circular mechanical portal suspended over a rocky alien landscape, an open black void at its center, segmented ivory metal armor and orange cables, tiny lone explorer beneath the ring for scale",
    "a colossal tilted narrow oval aperture, segmented metal becoming curled living membranes and branching pale coral, deep open black slit, orange tendrils, tiny explorer below",
    "a colossal reopened organic portal, circular open black void surrounded by scalloped ivory cartilage and turquoise coral folds, orange branching roots, tiny explorer beneath it",
]
NEGATIVE = "photograph, 3d render, glossy plastic, soft shading, blurry, muddy, washed out, pastel, text, lettering, watermark, logo, simple icon, flat white ring, gray monochrome"
REFINED_SUBJECT = ("an immense hollow alien portal with a broad perforated ivory rim and a dark teal mechanical exoskeleton, "
                   "a vast empty unobstructed black opening through its center, asymmetrical porous structures and curled cables around the rim, "
                   "a tiny lone explorer standing beneath it, small terracotta orange nebula wisps in the lower left, "
                   "deep black space surrounding the portal, richly detailed hand drawn science fiction art")


def node(kind, **inputs):
    return {"class_type": kind, "inputs": inputs}


def stills_graph(refine=False):
    g = {"1": node("CheckpointLoaderSimple", ckpt_name="sd_xl_base_1.0.safetensors"),
         "4": node("EmptyLatentImage", width=WIDTH, height=HEIGHT, batch_size=1),
         "20": node("LoadImage", image="anchor.png"),
         "21": node("ControlNetLoader", control_net_name="qr-sdxl-comfy.safetensors")}
    outputs = []
    for i, weight in enumerate((1.1, 1.1, 1.1) if refine else (0.0, 0.7, 1.1)):
        b = 100 + i * 10
        s = lambda offset: str(b + offset)
        g[s(0)] = node("LoraLoader", model=["1", 0], clip=["1", 1],
                       lora_name="xl_more_art-full_v1.safetensors", strength_model=weight, strength_clip=weight)
        g[s(1)] = node("CLIPTextEncode", clip=[s(0), 1], text=(REFINED_SUBJECT if refine else SUBJECTS[0]) + ", " + STYLE)
        g[s(2)] = node("CLIPTextEncode", clip=[s(0), 1], text=NEGATIVE + (", spokes, wheel, hub, clock, radial bars, solid orange background" if refine else ""))
        g[s(3)] = node("ControlNetApplyAdvanced", positive=[s(1), 0], negative=[s(2), 0],
                       control_net=["21", 0], image=["20", 0], strength=(0.25, 0.4, 0.55)[i] if refine else 0.65,
                       start_percent=0.0, end_percent=0.85, vae=["1", 2])
        g[s(4)] = node("KSampler", model=[s(0), 0], positive=[s(3), 0], negative=[s(3), 1],
                       latent_image=["4", 0], seed=7301, steps=32, cfg=7.0,
                       sampler_name="dpmpp_2m", scheduler="karras", denoise=1.0)
        g[s(5)] = node("VAEDecode", samples=[s(4), 0], vae=["1", 2])
        outputs.append([s(5), 0])
    g["200"] = node("ImageBatch", image1=outputs[0], image2=outputs[1])
    g["201"] = node("ImageBatch", image1=["200", 0], image2=outputs[2])
    g["11"] = node("SaveImage", images=["201", 0], filename_prefix="brain/stills")
    return g


def animation_graph(weight, denoise, control, cadence):
    g = json.loads((APP / "workflows/sdxl-feedback.api.json").read_text())
    del g["4"], g["5"]
    g["20"] = node("LoadImage", image="anchor.png")
    g["6"] = node("ImageCrop", image=["20", 0], width=WIDTH, height=HEIGHT, x=0, y=0)
    g["21"] = node("LoraLoader", model=["1", 0], clip=["1", 1],
                   lora_name="xl_more_art-full_v1.safetensors", strength_model=weight, strength_clip=weight)
    g["22"] = node("ControlNetLoader", control_net_name="qr-sdxl-comfy.safetensors")
    batch = None
    for i in range(COUNT):
        crop = str(100 + i)
        slot = i + 1
        g[crop] = node("ImageCrop", image=["20", 0], width=WIDTH, height=HEIGHT,
                       x=(slot % PACK_COLUMNS)*WIDTH, y=(slot // PACK_COLUMNS)*HEIGHT)
        if batch is None:
            batch = [crop, 0]
        else:
            key = str(200 + i)
            g[key] = node("ImageBatch", image1=batch, image2=[crop, 0])
            batch = [key, 0]
    for k in ("2", "3", "12"):
        g[k]["inputs"]["clip"] = ["21", 1]
    g["2"]["inputs"]["text"] = REFINED_SUBJECT + ", " + STYLE
    g["3"]["inputs"]["text"] = NEGATIVE + ", spokes, wheel, hub, clock, solid orange background"
    g["7"]["inputs"].update(max_frames=COUNT, seed=7301)
    g["8"]["inputs"].update(zoom="0:(1.001)", rotation_3d_z="0:(0)")
    g["9"]["inputs"]["schedule"] = f"0:({denoise})"
    g["12"]["inputs"]["prompts"] = "\n".join(f"{f}: {subject}, {STYLE}" for f, subject in zip((0, 23, 47), [REFINED_SUBJECT, *SUBJECTS[1:]]))
    g["10"]["inputs"].update(model=["21", 0], steps=30, cfg=7.0,
        control_net=["22", 0], control_image=batch, control_strength=control,
        noise=0.025, sharpen=0.35, color_coherence=0.25,
        cadence=cadence, seed_mode="increment")
    return g


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("stills", "stills-refined", "animate"))
    p.add_argument("--anchor", type=Path)
    p.add_argument("--weight", type=float, default=1.1)
    p.add_argument("--denoise", type=float, default=0.55)
    p.add_argument("--control", type=float, default=0.75)
    p.add_argument("--cadence", type=int, default=1)
    p.add_argument("--label", default="feedback-v001")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.mode.startswith("stills"):
        refine = args.mode == "stills-refined"
        graph, count, name = stills_graph(refine), 3, "stills-control-sweep" if refine else "stills-lora-sweep"
        source = PROJECT / "references/assets/guide-v001/frames/0000.png"
    else:
        if not args.anchor or not args.anchor.is_file():
            p.error("animate needs an existing --anchor PNG")
        graph, count, name = animation_graph(args.weight, args.denoise, args.control, args.cadence), COUNT, args.label
        source = PROJECT / f"references/assets/{name}-packed.png"
        if not args.dry_run:
            from PIL import Image
            if source.exists():
                raise FileExistsError(source)
            packed = Image.new("RGB", (WIDTH*PACK_COLUMNS, HEIGHT*((COUNT+PACK_COLUMNS)//PACK_COLUMNS)))
            with Image.open(args.anchor) as anchor:
                if anchor.size != (WIDTH, HEIGHT):
                    raise ValueError("Anchor dimensions do not match")
                packed.paste(anchor.convert("RGB"), (0, 0))
            with Image.open(PROJECT / "references/assets/guide-v001/strip.png") as guide:
                for i in range(COUNT):
                    slot = i + 1
                    packed.paste(guide.crop((i*WIDTH, 0, (i+1)*WIDTH, HEIGHT)),
                                 ((slot % PACK_COLUMNS)*WIDTH, (slot // PACK_COLUMNS)*HEIGHT))
            packed.save(source)
    if args.dry_run:
        print(json.dumps(graph, indent=2))
        return
    result = serverless_client.submit(PROJECT, name, graph, count, source=source,
        lineage={"study": "brain-entity-style", "source_reference": "YouTube drUsc1Vfy6s, 36–42s",
                 "original_composition": True, "settings": vars(args) | {"anchor": str(args.anchor)}})
    print(result)


if __name__ == "__main__":
    main()
