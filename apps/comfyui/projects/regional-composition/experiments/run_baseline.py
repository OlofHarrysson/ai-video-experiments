# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Native SDXL composition graphs and explicit submit/collect receipts.

Graph construction follows the official noisy-latent example and pinned core
node implementations listed in references/README.md and the research note.
Run with uv run --script; no Deforum runner or custom node dependency.
"""
import argparse
import hashlib
import json
import shlex
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
CHECKPOINT = "sd_xl_base_1.0.safetensors"
MODEL_HASH = "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b"
STYLE = "painterly fantasy illustration, warm golden light from upper left, coherent perspective, grassy ground plane"
BACKGROUND = "distant mountains, open meadow, golden sky, " + STYLE
OBJECTS = ["one small red tin robot standing on grass, full body, " + STYLE,
           "one blue glass tree rooted in grass, translucent branching canopy, " + STYLE]
NEGATIVE = "text, watermark, duplicate objects, cropped objects"
REGIONS = [(64, 384, 384, 512), (576, 384, 384, 512)]
WIDTH = HEIGHT = 1024
STEPS, CFG = 28, 6.5


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def request(base, path, payload=None, binary=False):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data,
                                 headers={"Content-Type": "application/json", "User-Agent": "comfyui-experiment/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read()
    return body if binary else json.loads(body)


class Graph:
    def __init__(self, prefix, seed_offset, background_strength=1.0, conditioning="area"):
        self.nodes = {}
        self.prefix = prefix
        self.seed = 21001 + seed_offset
        checkpoint = self.add("CheckpointLoaderSimple", ckpt_name=CHECKPOINT)
        self.model, self.clip, self.vae = checkpoint, [checkpoint[0], 1], [checkpoint[0], 2]
        self.negative = self.text(NEGATIVE)
        self.background = self.text(BACKGROUND)
        self.objects = [self.text(p) for p in OBJECTS]
        self.regional = self.background
        if background_strength != 1.0:
            self.regional = self.add("ConditioningSetAreaStrength", conditioning=self.background,
                                     strength=background_strength)
        for cond, (x, y, width, height) in zip(self.objects, REGIONS):
            if conditioning == "area":
                local = self.add("ConditioningSetArea", conditioning=cond, x=x, y=y,
                                 width=width, height=height, strength=1.0)
            else:
                local = self.add("ConditioningSetMask", conditioning=cond,
                                 mask=self.mask((x, y, width, height), soft=True),
                                 set_cond_area="default", strength=1.0)
            self.regional = self.add("ConditioningCombine", conditioning_1=self.regional,
                                     conditioning_2=local)

    def add(self, node_type, **inputs):
        node_id = str(len(self.nodes) + 1)
        self.nodes[node_id] = {"class_type": node_type, "inputs": inputs}
        return [node_id, 0]

    def text(self, text):
        return self.add("CLIPTextEncode", clip=self.clip, text=text)

    def empty(self, width=WIDTH, height=HEIGHT):
        return self.add("EmptyLatentImage", width=width, height=height, batch_size=1)

    def sample(self, latent, positive, seed, denoise=1.0, steps=STEPS):
        return self.add("KSampler", model=self.model, positive=positive,
                        negative=self.negative, latent_image=latent, seed=seed,
                        steps=steps, cfg=CFG, sampler_name="euler", scheduler="normal",
                        denoise=denoise)

    def partial(self, latent, positive, seed, start, end):
        return self.add("KSamplerAdvanced", model=self.model, positive=positive,
                        negative=self.negative, latent_image=latent, noise_seed=seed,
                        steps=STEPS, cfg=CFG, sampler_name="euler", scheduler="normal",
                        start_at_step=start, end_at_step=end,
                        add_noise="enable" if start == 0 else "disable",
                        return_with_leftover_noise="enable" if end < STEPS else "disable")

    def decode(self, latent):
        return self.add("VAEDecode", samples=latent, vae=self.vae)

    def save(self, image, label):
        self.add("SaveImage", images=image, filename_prefix=f"{self.prefix}/{label}")
        return image

    def mask(self, region, soft=False):
        x, y, width, height = region
        canvas = self.add("SolidMask", value=0.0, width=WIDTH, height=HEIGHT)
        patch = self.add("SolidMask", value=1.0, width=width, height=height)
        if soft:
            patch = self.add("FeatherMask", mask=patch, left=32, top=32, right=32, bottom=32)
        return self.add("MaskComposite", destination=canvas, source=patch, x=x, y=y, operation="add")

    def build(self, variant, split=7, insertion=0.85):
        if variant == "smoke":
            self.save(self.decode(self.sample(self.empty(512, 512), self.background,
                                              self.seed, steps=4)), "smoke")
        elif variant == "regional":
            self.save(self.decode(self.sample(self.empty(), self.regional, self.seed)), "regional")
        elif variant == "noisy":
            latent = self.partial(self.empty(), self.background, self.seed, 0, split)
            self.save(self.decode(latent), "background-noisy")
            for i, (cond, region) in enumerate(zip(self.objects, REGIONS)):
                x, y, width, height = region
                patch = self.partial(self.empty(width, height), cond, self.seed + i + 1, 0, split)
                self.save(self.decode(patch), f"object-{i+1}-noisy")
                latent = self.add("LatentComposite", samples_to=latent, samples_from=patch,
                                  x=x, y=y, feather=32)
            self.save(self.decode(latent), "composite-noisy")
            self.add("SaveLatent", samples=latent, filename_prefix=f"{self.prefix}/composite-noisy")
            self.save(self.decode(self.partial(latent, self.regional, 0, split, STEPS)), "noisy-final")
        elif variant == "layered":
            image = self.save(self.decode(self.sample(self.empty(), self.background, self.seed)), "background")
            for i, (cond, region) in enumerate(zip(self.objects, REGIONS)):
                mask, composite_mask = self.mask(region), self.mask(region, soft=True)
                self.save(self.add("MaskToImage", mask=mask), f"object-{i+1}-sampling-mask")
                self.save(self.add("MaskToImage", mask=composite_mask), f"object-{i+1}-composite-mask")
                encoded = self.add("VAEEncodeForInpaint", pixels=image, vae=self.vae,
                                   mask=mask, grow_mask_by=6)
                patch = self.decode(self.sample(encoded, cond, self.seed+i+1, denoise=insertion))
                self.save(patch, f"object-{i+1}-raw-decoded")
                image = self.add("ImageCompositeMasked", destination=image, source=patch,
                                 x=0, y=0, resize_source=False, mask=composite_mask)
                self.save(image, f"after-object-{i+1}")
            encoded = self.add("VAEEncode", pixels=image, vae=self.vae)
            final = self.decode(self.sample(encoded, self.regional, self.seed+3, denoise=0.15))
            self.save(final, "layered-finished")
        else:
            raise ValueError(variant)
        # Prune unconnected conditioning nodes from variants that do not use them.
        keep = set()
        def visit(node_id):
            if node_id in keep:
                return
            keep.add(node_id)
            for value in self.nodes[node_id]["inputs"].values():
                if isinstance(value, list):
                    visit(value[0])
        for node_id, node in self.nodes.items():
            if node["class_type"] in ("SaveImage", "SaveLatent"):
                visit(node_id)
        return {k: v for k, v in self.nodes.items() if k in keep}


def validate(graph, schema):
    """Check required fields, links, output types and live enum membership."""
    for node_id, node in graph.items():
        spec = schema[node["class_type"]]
        required = spec["input"].get("required", {})
        fields = {**required, **spec["input"].get("optional", {})}
        assert set(required) <= node["inputs"].keys(), (node_id, "missing required input")
        for key, value in node["inputs"].items():
            kind, *options = fields[key]
            if isinstance(value, list):
                source, slot = value
                actual = schema[graph[source]["class_type"]]["output"][slot]
                assert actual == kind, (node_id, key, actual, kind)
            else:
                choices = kind if isinstance(kind, list) else (options[0].get("options") if kind == "COMBO" else None)
                if choices:
                    assert value in choices, (node_id, key, value)


def ui_workflow(graph, schema):
    """Build an editable native graph with sockets and widgets from live schemas."""
    nodes, links, depths, rows = [], [], {}, {}
    for key, node in graph.items():
        spec = schema[node["class_type"]]
        fields = {**spec["input"].get("required", {}), **spec["input"].get("optional", {})}
        upstream = [v[0] for v in node["inputs"].values() if isinstance(v, list)]
        depth = max((depths[v]+1 for v in upstream), default=0)
        depths[key] = depth
        row = rows.get(depth, 0); rows[depth] = row + 1
        entry = {"id": int(key), "type": node["class_type"], "pos": [depth*360, row*600],
                 "size": [330, 450], "flags": {}, "order": len(nodes), "mode": 0,
                 "inputs": [], "outputs": [], "properties": {"Node name for S&R": node["class_type"]},
                 "widgets_values": []}
        for name, field in fields.items():
            if name not in node["inputs"]:
                continue
            value = node["inputs"][name]
            if isinstance(value, list):
                link_id = len(links)+1
                links.append([link_id, int(value[0]), value[1], int(key), len(entry["inputs"]), field[0]])
                entry["inputs"].append({"name": name, "type": field[0], "link": link_id})
            else:
                entry["widgets_values"].append(value)
                if len(field)>1 and field[1].get("control_after_generate"):
                    entry["widgets_values"].append("fixed")
        for slot, kind in enumerate(spec["output"]):
            entry["outputs"].append({"name": spec.get("output_name", spec["output"])[slot],
                                     "type": kind, "links": [], "slot_index": slot})
        nodes.append(entry)
    by_id = {n["id"]: n for n in nodes}
    for link_id, source, slot, target, target_slot, kind in links:
        by_id[source]["outputs"][slot]["links"].append(link_id)
    return {"last_node_id": max(by_id), "last_link_id": len(links), "nodes": nodes,
            "links": links, "groups": [], "config": {}, "extra": {}, "version": 0.4}


def collect(folder, deployment):
    receipt = json.loads((folder/"submission.json").read_text())
    base, prompt_id = deployment["base_url"], receipt["prompt_id"]
    deadline = time.monotonic()+1800
    while True:
        history = request(base, "/history/"+prompt_id).get(prompt_id)
        if history:
            write_json(folder/"history.json", history)
            if history.get("status", {}).get("status_str") == "error":
                raise RuntimeError(f"Generation failed; inspect {folder/'history.json'}")
            if history.get("status", {}).get("completed"):
                break
        if time.monotonic()>deadline:
            raise TimeoutError("History wait expired; collect the same prompt_id, do not resubmit")
        time.sleep(3)
    outputs = folder/"outputs"; outputs.mkdir(exist_ok=True)
    files = []
    for node_id, output in history["outputs"].items():
        for category in ("images", "latents"):
            for asset in output.get(category, []):
                content = request(base, "/view?"+urllib.parse.urlencode(asset), binary=True)
                name = Path(asset["filename"]).name
                target = outputs/name
                if target.exists() and target.read_bytes() != content:
                    raise RuntimeError("Refusing to replace an archived output")
                target.write_bytes(content)
                item = {"node_id": node_id, **asset, "local": str(target.relative_to(folder)),
                        "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
                if category == "images":
                    with Image.open(target) as im:
                        im.load(); item["size"] = list(im.size)
                files.append(item)
    remote_paths = [deployment["remote_output"]+"/"+a.get("subfolder", "")+"/"+a["filename"] for a in files]
    result = subprocess.run(["ssh", "-i", deployment["ssh_identity"], "-p", str(deployment["ssh_port"]),
                             "root@"+deployment["ssh_host"], "sha256sum "+" ".join(map(shlex.quote, remote_paths))],
                            check=True, capture_output=True, text=True, timeout=60)
    remote_hashes = [line.split()[0] for line in result.stdout.splitlines()]
    assert remote_hashes == [a["sha256"] for a in files], "Remote/local hash mismatch"
    write_json(folder/"files.json", files)
    receipt.update(completed_at=datetime.now(timezone.utc).isoformat(), outputs=len(files), remote_hashes_verified=True)
    write_json(folder/"submission.json", receipt)
    print(json.dumps({"folder": str(folder), "outputs": len(files), "verified": True}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["run", "collect"])
    parser.add_argument("--deployment", type=Path, required=True)
    parser.add_argument("--variant", choices=["smoke", "regional", "noisy", "layered"])
    parser.add_argument("--seed-offset", type=int, default=0)
    parser.add_argument("--split", type=int, default=7)
    parser.add_argument("--insertion", type=float, default=0.85)
    parser.add_argument("--background-strength", type=float, default=1.0)
    parser.add_argument("--conditioning", choices=["area", "mask"], default="area")
    parser.add_argument("--folder", type=Path)
    args = parser.parse_args()
    deployment = json.loads(args.deployment.read_text())
    if deployment.get("status") == "deleted":
        raise RuntimeError("This deployment is closed; select the current session receipt")
    if args.action == "collect":
        collect(args.folder, deployment); return
    assert args.variant, "--variant is required for run"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    label = f"{stamp}-{args.variant}-seed{21001+args.seed_offset}"
    folder = PROJECT/"runs"/label; folder.mkdir(parents=True)
    graph = Graph("regional-composition/"+label, args.seed_offset, args.background_strength, args.conditioning).build(args.variant, args.split, args.insertion)
    schema = request(deployment["base_url"], "/object_info")
    validate(graph, schema)
    ui = ui_workflow(graph, schema)
    write_json(folder/"workflow.api.json", graph)
    write_json(folder/"workflow.json", ui)
    write_json(folder/"node-schemas.json", {n["class_type"]: schema[n["class_type"]] for n in graph.values()})
    write_json(folder/"system-stats.json", request(deployment["base_url"], "/system_stats"))
    receipt = {"pod_id": deployment["pod_id"], "variant": args.variant,
               "seed_offset": args.seed_offset, "split": args.split, "insertion": args.insertion,
               "background_strength": args.background_strength,
               "conditioning": args.conditioning,
               "checkpoint_sha256": MODEL_HASH, "submitted_at": datetime.now(timezone.utc).isoformat()}
    write_json(folder/"submission.json", receipt)
    # Submission is intentionally never retried: an ambiguous HTTP failure may
    # have queued work. Inspect queue/history before deciding what to do next.
    try:
        response = request(deployment["base_url"], "/prompt",
                           {"prompt": graph, "client_id": label, "extra_data": {"extra_pnginfo": {"workflow": ui}}})
    except Exception as error:
        write_json(folder/"submission-error.json", {"error": str(error), "action": "Inspect queue/history before retry"})
        raise
    write_json(folder/"submit-response.json", response)
    assert response.get("prompt_id") and not response.get("node_errors"), response
    receipt["prompt_id"] = response["prompt_id"]
    write_json(folder/"submission.json", receipt)
    print(json.dumps({"submitted": receipt["prompt_id"], "folder": str(folder)}), flush=True)
    collect(folder, deployment)


if __name__ == "__main__":
    main()
