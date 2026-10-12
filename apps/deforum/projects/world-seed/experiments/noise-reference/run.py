"""World Seed noise/reference study; frozen cases, recurrent RGB feedback and receipts."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.feedback import render_paintings
from deforum_lab.rendering.graphs import node, repaint_graph
from deforum_lab.rendering.schedules import recipe

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
PROJECT = HERE.parents[1]
OUT = PROJECT / "exports/v002"
INSTRUCTION = "Preserve this exact scene and its composition, all major objects, their silhouettes, scale and positions. Re-render the same view with clearly resolved material relief and fine surface detail. "


def transform(graph, config, seconds):
    mode = config.get("reference_mode", "none")
    sampler = config.get("sampler", "euler")
    require(sampler in ("euler", "euler_ancestral"), "Unknown study sampler")
    if sampler == "euler_ancestral":
        require(mode != "native", "Native edit uses its frozen Euler recipe")
        graph["42"] = node(
            "SamplerEulerAncestral", eta=config["sampler_eta"], s_noise=1.0
        )
    if mode == "none":
        return
    require(mode in ("native", "hybrid"), "Unknown reference mode")
    prompt = graph["4"]["inputs"]["text"]
    graph["4"] = node(
        "Krea2EditGroundedEncode",
        clip=["2", 0],
        prompt=config.get("reference_instruction", INSTRUCTION) + prompt,
        image=["20", 0],
        grounding_px=config.get("grounding_px", 768),
    )
    graph["50"] = node(
        "LoraLoaderModelOnly",
        model=["1", 0],
        lora_name="krea2_identity_edit_v1_2.safetensors",
        strength_model=config.get("edit_strength", 1.0),
    )
    target = ["24", 0]
    if mode == "native":
        graph["6"] = node("EmptySD3LatentImage", width=1536, height=1024, batch_size=1)
        target = ["6", 0]
        graph["9"] = node(
            "KSampler",
            model=["51", 0],
            positive=["4", 0],
            negative=["5", 0],
            latent_image=target,
            seed=graph["9"]["inputs"]["noise_seed"],
            steps=8,
            cfg=1.0,
            sampler_name="euler",
            scheduler="simple",
            denoise=1.0,
        )
        del graph["42"], graph["43"]
    else:
        graph["9"]["inputs"]["model"] = ["51", 0]
    graph["51"] = node(
        "Krea2EditModelPatch",
        model=["50", 0],
        source_latent=["24", 0],
        vae=["3", 0],
        source_image=["20", 0],
        target_latent=target,
        fit_mode="fit",
        ref_boost=config.get("ref_boost", 1.0),
        ref_boost_a=1.0,
    )


def make_graph(config, frame):
    scene, sigmas = recipe(config, frame / 24)
    g = repaint_graph(scene["prompt"], config["seed"] + frame // 12, sigmas)
    transform(g, config, frame / 24)
    g["11"]["inputs"]["filename_prefix"] = (
        "world-seed/noise-reference/" + config["case"]
    )
    return g


def prepare(config):
    root = OUT / config["case"]
    save(root / "config.json", config)
    source = APP / config["initial_image"]
    require(sha(source) == config["initial_sha256"], "Opening changed")
    copy_verified(source, root / "anchors/0000.png")


def check(config):
    root = OUT / config["case"]
    require(read(root / "config.json") == config, "Frozen configuration differs")
    require(
        sha(root / "anchors/0000.png") == config["initial_sha256"], "Opening differs"
    )
    jobs = []
    for previous, frame in zip(
        config["painting_frames"], config["painting_frames"][1:]
    ):
        row = read(root / f"anchor-{frame:04d}.json")
        run = OUT / row["run"]
        parent = root / f"anchors/{previous:04d}.png"
        source = root / f"warped-inputs/{frame:04d}.png"
        target = root / f"anchors/{frame:04d}.png"
        require(row["parent_sha256"] == sha(parent), "Feedback parent differs")
        require(
            row["initialization_sha256"] == sha(source) == sha(run / "anchor.png"),
            "Initialization differs",
        )
        require(
            row["output_sha256"] == sha(target) == sha(run / "frames/0000.png"),
            "Output differs",
        )
        expected = make_graph(config, frame)
        require(read(run / "workflow.api.json") == expected, "Requested graph differs")
        upload = read(run / "upload.json")
        expected["20"]["inputs"]["image"] = "/".join(
            filter(None, [upload.get("subfolder"), upload["name"]])
        )
        require(
            read(run / "workflow.executed.json") == expected, "Executed graph differs"
        )
        history = read(run / "history.json")
        require(
            history["status"]["completed"]
            and history["status"]["status_str"] == "success",
            "Unsuccessful job",
        )
        require(history["prompt"][2] == expected, "History graph differs")
        require(
            history["prompt"][1] == read(run / "submission.json")["prompt_id"],
            "Job ID differs",
        )
        with Image.open(parent) as im:
            wanted = warp_at_time(
                np.asarray(im.convert("RGB")),
                previous / 24,
                frame / 24,
                config["phrases"],
            )
        with Image.open(source) as im:
            require(
                np.array_equal(np.asarray(im.convert("RGB")), wanted), "Warp differs"
            )
        with Image.open(target) as im:
            embedded = json.loads(im.info["prompt"])
            for n in embedded.values():
                n.pop("is_changed", None)
            require(embedded == expected, "Embedded PNG graph differs")
            require(im.size == (1536, 1024), "Output dimensions differ")
        jobs.append(
            {"frame": frame, "prompt_id": history["prompt"][1], "sha256": sha(target)}
        )
    save(root / "study-check.json", {"verified": True, "jobs": jobs})
    return jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["render", "check"])
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--deployment", type=Path)
    parser.add_argument("--ids", nargs="+")
    args = parser.parse_args()
    cases = read(args.matrix)["cases"]
    if args.ids:
        cases = [c for c in cases if c["case"] in args.ids]
        require(len(cases) == len(args.ids), "Unknown case")
    for config in cases:
        require(
            config["case"].startswith("nr-")
            and Path(config["case"]).name == config["case"],
            "Invalid case",
        )
        require(config["cfg"] == 1 and config["cadence"] == 12, "Study controls differ")
        if args.stage == "render":
            require(args.deployment is not None, "Explicit deployment required")
            prepare(config)
            render_paintings(
                config,
                OUT,
                PodClient.from_path(args.deployment),
                first_frame=12,
                last_frame=config["painting_frames"][-1],
                run_prefix=config["case"],
                filename_prefix="world-seed/noise-reference/" + config["case"],
                graph_transform=transform,
            )
        jobs = check(config)
        print(f"VERIFIED {config['case']}: {len(jobs)} paintings", flush=True)


if __name__ == "__main__":
    main()
