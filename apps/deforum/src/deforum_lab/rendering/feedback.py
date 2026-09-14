"""Recurrent painting execution with explicit output and client ownership."""

from itertools import pairwise

import numpy as np
from PIL import Image

from deforum_lab.image.warps import warp_at_time
from deforum_lab.records import copy_verified, read, require, save, sha

from .graphs import repaint_graph
from .schedules import recipe


def render_paintings(
    config,
    output,
    client,
    *,
    first_frame,
    last_frame,
    run_prefix,
    filename_prefix,
    fps=24,
    graph_transform=None,
):
    cadence = config.get("cadence", 12)
    require(
        isinstance(cadence, int) and cadence > 0 and fps % cadence == 0,
        "Cadence must be a positive integer divisor of FPS",
    )
    positions = config.get("painting_frames", list(range(0, last_frame + 1, cadence)))
    require(
        len(positions) >= 2
        and positions[0] == 0
        and all(type(f) is int for f in positions)
        and all(a < b for a, b in pairwise(positions)),
        "Expected strictly increasing painting frames starting at zero",
    )
    require(
        first_frame in positions[1:]
        and last_frame in positions
        and last_frame >= first_frame,
        "Expected ordered painting boundaries",
    )
    root = output / config["case"]
    save(root / "config.json", config)
    for previous_frame, frame in pairwise(positions):
        if not first_frame <= frame <= last_frame:
            continue
        seconds = frame / fps
        parent = root / f"anchors/{previous_frame:04d}.png"
        target = root / f"anchors/{frame:04d}.png"
        source = root / f"warped-inputs/{frame:04d}.png"
        source.parent.mkdir(exist_ok=True)
        scene, sigmas = recipe(config, seconds)
        seed = config.get("seeds_by_frame", {}).get(
            str(frame), config["seed"] + frame // cadence
        )
        graph = repaint_graph(scene["prompt"], seed, sigmas)
        graph["9"]["inputs"]["cfg"] = config.get("cfg", 1.0)
        if graph_transform is not None:
            graph_transform(graph, config, seconds)
        graph["11"]["inputs"]["filename_prefix"] = filename_prefix
        receipt = root / f"anchor-{frame:04d}.json"
        expected = {
            "frame": frame,
            "seconds": seconds,
            "seed": seed,
            "scene": scene["name"],
            "sigmas": sigmas,
            "parent_sha256": sha(parent),
        }
        if receipt.exists():
            row = read(receipt)
            run = output / row["run"]
            require(
                all(row.get(k) == v for k, v in expected.items()),
                "Saved painting settings differ",
            )
            require(
                row["output_sha256"] == sha(target) == sha(run / "frames/0000.png"),
                "Saved painting output differs",
            )
            require(
                row["initialization_sha256"] == sha(source) == sha(run / "anchor.png"),
                "Saved painting initialization differs",
            )
            require(
                read(run / "workflow.api.json") == graph, "Saved painting graph differs"
            )
            continue
        with Image.open(parent) as im:
            rgb = np.asarray(im.convert("RGB"))
        Image.fromarray(
            warp_at_time(rgb, previous_frame / fps, seconds, config["phrases"])
        ).save(source)
        run = client.submit_once(
            output,
            f"{run_prefix}-{frame:04d}",
            graph,
            source,
            {
                "parent_sha256": sha(parent),
                "initialization_sha256": sha(source),
                "frame": frame,
                "seconds": seconds,
                "scene": scene["name"],
                "sigma_start": sigmas[0],
            },
        )
        copy_verified(run / "frames/0000.png", target)
        save(
            receipt,
            {
                "run": str(run.relative_to(output)),
                **expected,
                "initialization_sha256": sha(source),
                "output_sha256": sha(target),
            },
        )
        print(f"Painting {frame}: noise {sigmas[0]:.2f}", flush=True)
