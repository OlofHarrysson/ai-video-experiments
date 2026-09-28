"""Project-specific structural injection probes using the shared Krea repaint graph."""

import argparse
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import sha
from deforum_lab.rendering.graphs import graph, repaint_graph

ROOT = Path(__file__).parent
FLOW_CORE = 125
FLOW_EDGE = 245
BASE = "A cinematic painterly view of a quiet tropical beach. Pale golden sand fills the lower foreground, a turquoise ocean and low distant rocky headland cross the middle distance, and a broad clear blue sky fills the upper half. Warm afternoon light from the upper left, tactile natural textures, coherent perspective, spacious composition, richly detailed and visually expressive."
BALL = (
    BASE
    + " A single airborne volleyball with curved stitched panels is suspended above the shoreline, naturally lit and integrated into the scene."
)
PROMPTS = {
    "generic": BASE,
    "ball": BALL,
    "ring": BASE
    + " An impossible floating ring of weathered sandstone forms a sculptural circular arch above the beach.",
    "triangle": BASE
    + " A triangular white fabric kite floats above the beach, its cloth catching the sunlight.",
}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def inject(source, kind, alpha, index, target):
    im = Image.open(source).convert("RGBA")
    if kind != "none" and alpha:
        guide = Image.open(ROOT / f"references/assets/{kind}/{index:03d}.png").convert(
            "RGBA"
        )
        assert guide.size == im.size
        a = np.asarray(guide.getchannel("A"), dtype=float)
        guide.putalpha(Image.fromarray(np.rint(a * alpha).astype("uint8")))
        im = Image.alpha_composite(im, guide)
    target.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(target)


def transport(source, index, target):
    """Move a broad image region using authored coordinates, without segmentation."""
    positions = json.loads((ROOT / "references/assets/guide.json").read_text())[
        "positions"
    ]
    before, after = positions[index - 1], positions[index]
    im = np.asarray(Image.open(source).convert("RGB"))
    yy, xx = np.mgrid[: im.shape[0], : im.shape[1]].astype(np.float32)
    distance = np.hypot(xx - after["x"], yy - after["y"])
    u = np.clip((distance - FLOW_CORE) / (FLOW_EDGE - FLOW_CORE), 0, 1)
    weight = 1 - u * u * (3 - 2 * u)
    mx = xx - (after["x"] - before["x"]) * weight
    my = yy - (after["y"] - before["y"]) * weight
    warped = cv2.remap(im, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
    target.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(warped).save(target)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["opening", "probes", "sequence"])
    p.add_argument("--deployment", type=Path, required=True)
    p.add_argument("--kind", default="circle")
    p.add_argument("--alpha", type=float, default=0.65)
    p.add_argument("--noise", type=float, default=0.6)
    p.add_argument("--prompt", default="ball")
    p.add_argument("--name")
    p.add_argument("--frames", type=int, default=16)
    p.add_argument(
        "--follow-alpha",
        type=float,
        help="Optional blend strength after the first painting",
    )
    p.add_argument(
        "--flow",
        action="store_true",
        help="Move a broad region along the authored guide path before blending",
    )
    a = p.parse_args()
    if not 1 <= a.frames <= 16 or not 0 <= a.alpha <= 1:
        p.error("frames must be 1–16 and alpha must be 0–1")
    if a.follow_alpha is not None and not 0 <= a.follow_alpha <= 1:
        p.error("follow-alpha must be 0–1")
    client = PodClient.from_path(a.deployment)
    (ROOT / "runs").mkdir(parents=True, exist_ok=True)
    opening = ROOT / "references/assets/opening.png"
    if a.stage == "opening":
        g = graph("krea", BASE, 7281)
        g["11"]["inputs"]["filename_prefix"] = "shape-injection/opening"
        run = client.submit_once(ROOT, "opening", g)
        opening.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / "frames/0000.png", opening)
        print("OPENING", run, flush=True)
        return
    if a.stage == "probes":
        cases = []
        for prompt in ["generic", "ball"]:
            for noise in [0.6, 0.85]:
                for alpha in [0, 0.45, 0.8]:
                    cases.append(
                        (
                            f"{prompt}-circle-a{alpha}-n{noise}",
                            "circle",
                            alpha,
                            noise,
                            prompt,
                        )
                    )
        for kind, prompt in [
            ("sphere", "ball"),
            ("ring", "ring"),
            ("triangle", "triangle"),
        ]:
            for alpha in [0, 0.8]:
                cases.append(
                    (f"{prompt}-{kind}-a{alpha}-n0.6", kind, alpha, 0.6, prompt)
                )
        for name, kind, alpha, noise, prompt in cases:
            out = ROOT / "exports/probes" / name
            source = out / "injected.png"
            inject(opening, kind, alpha, 0, source)
            g = repaint_graph(
                PROMPTS[prompt],
                7282,
                [s * noise / 0.6 for s in [0.6, 0.512844085693, 0.310901075602, 0]],
            )
            g["11"]["inputs"]["filename_prefix"] = "shape-injection/" + name
            run = client.submit_once(
                ROOT,
                name,
                g,
                source,
                {
                    "kind": kind,
                    "alpha": alpha,
                    "noise": noise,
                    "prompt_key": prompt,
                    "guide_frame": 0,
                    "source_sha256": sha(opening),
                    "injected_sha256": sha(source),
                },
            )
            shutil.copyfile(run / "frames/0000.png", out / "output.png")
            save(
                out / "case.json",
                {
                    "name": name,
                    "kind": kind,
                    "alpha": alpha,
                    "noise": noise,
                    "prompt_key": prompt,
                    "run": str(run.relative_to(ROOT)),
                },
            )
            print("DONE", name, flush=True)
        return
    name = a.name or f"{a.kind}-a{a.alpha}-n{a.noise}-{a.prompt}"
    out = ROOT / "exports/sequences" / name
    out.mkdir(parents=True, exist_ok=True)
    parent = opening
    for i in range(a.frames):
        source = out / f"injected/{i:03d}.png"
        initialized = parent
        if a.flow and i:
            initialized = out / f"warped/{i:03d}.png"
            transport(parent, i, initialized)
        alpha = a.follow_alpha if i and a.follow_alpha is not None else a.alpha
        inject(initialized, a.kind, alpha, i, source)
        g = repaint_graph(
            PROMPTS[a.prompt],
            7300 + i,
            [s * a.noise / 0.6 for s in [0.6, 0.512844085693, 0.310901075602, 0]],
        )
        g["11"]["inputs"]["filename_prefix"] = "shape-injection/" + name
        run = client.submit_once(
            ROOT,
            f"{name}-{i:03d}",
            g,
            source,
            {
                "kind": a.kind,
                "alpha": alpha,
                "noise": a.noise,
                "prompt_key": a.prompt,
                "guide_frame": i,
                "parent_sha256": sha(parent),
                "injected_sha256": sha(source),
                **(
                    {
                        "transport": "authored-local-translation",
                        "flow_core": FLOW_CORE,
                        "flow_edge": FLOW_EDGE,
                        "warped_sha256": sha(initialized),
                    }
                    if a.flow
                    else {}
                ),
            },
        )
        target = out / f"frames/{i:03d}.png"
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(run / "frames/0000.png", target)
        parent = target
        print("FRAME", name, i, flush=True)
    save(
        out / "sequence.json",
        {
            "name": name,
            "kind": a.kind,
            "alpha": a.alpha,
            "follow_alpha": a.follow_alpha,
            "noise": a.noise,
            "prompt": PROMPTS[a.prompt],
            "frames": a.frames,
            "fps": 4,
            "flow": a.flow,
            "feedback": "Every generated image initializes the next painting after shape compositing; no masks in sampler and no regional prompts.",
        },
    )


if __name__ == "__main__":
    main()
