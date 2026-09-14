"""Verify the established sixteen-painting, 24 fps RIFE delivery contract."""

from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.records import read, require, sha

PIN = "bbfd2ea90910789a860ea3e2b32a240cd577b75e"


def frame_plan(count, final_holds=None, *, multiplier):
    """Each pair owns its left anchor; the final anchor appears just once."""
    if count < 2 or multiplier < 2:
        raise ValueError("At least two frames and multiplier >= 2 required")
    if final_holds is None:
        final_holds = multiplier - 1
    rows = []
    for index in range(count - 1):
        rows.append({"kind": "anchor", "source_index": index})
        for numerator in range(1, multiplier):
            rows.append(
                {
                    "kind": "interpolation",
                    "source_pair": [index, index + 1],
                    "timestep": f"{numerator}/{multiplier}",
                }
            )
    rows.append({"kind": "anchor", "source_index": count - 1})
    rows.extend(
        {"kind": "final_hold", "source_index": count - 1} for _ in range(final_holds)
    )
    return rows


def pixels(path, size):
    with Image.open(path) as im:
        require(
            im.format == "PNG" and im.mode == "RGB" and im.size == size,
            f"Expected {size} RGB PNG: {path}",
        )
        return np.array(im)


def inventory(folder, indices):
    expected = [f"{i:04d}.png" for i in indices]
    actual = sorted(p.name for p in folder.glob("*.png"))
    require(
        actual == expected,
        f"Incomplete or unexpected PNG inventory: {folder} "
        f"(found {len(actual)}, expected {len(expected)})",
    )


def check_rife(root, stage, *, size, fps, cadence, frame_count):
    FPS, CADENCE, FRAME_COUNT, SIZE = fps, cadence, frame_count, size
    anchors = frame_count // cadence
    require(frame_count % cadence == 0, "Expected complete painting intervals")
    case = root.name
    section = root / f"section-{anchors:03d}"
    target = section / ("pair" if stage == "pair" else "rife")
    manifest = read(target / "manifest.json")
    require(
        manifest["status"] == "complete"
        and manifest["anchors_verified"] is True
        and manifest["source_hashes_and_mtimes_preserved"] is True,
        f"Incomplete RIFE: {case}/{stage}",
    )
    require(
        manifest["mode"] == ("first_pair" if stage == "pair" else "full"),
        "RIFE mode differs",
    )
    for key, expected in {
        "source_fps": fps / cadence,
        "output_fps": float(fps),
        "multiplier": cadence,
        "timesteps": [f"{i}/{cadence}" for i in range(1, cadence)],
        "scale": 1.0,
        "scale_list": [16, 8, 4, 2, 1],
        "scene_detection": False,
        "static_frame_skipping": False,
        "ensemble": False,
        "fastmode": True,
    }.items():
        require(
            manifest["settings"][key] == expected, f"RIFE setting differs: {case}/{key}"
        )
    require(
        manifest["provenance"]["model"] == "RIFE 4.25"
        and manifest["provenance"]["commit"] == PIN,
        "RIFE implementation differs",
    )
    require(len(manifest["sources"]) == anchors, "RIFE source count differs")
    inventory(section / "sources", range(anchors))
    for i, row in enumerate(manifest["sources"]):
        source = section / f"sources/{i:04d}.png"
        require(
            Path(row["file"]).resolve() == source.resolve()
            and row["size"] == list(SIZE)
            and row["mtime_ns"] == source.stat().st_mtime_ns
            and row["sha256"]
            == sha(source)
            == sha(root / f"anchors/{i * CADENCE:04d}.png"),
            f"RIFE source changed: {case}/{i}",
        )
    holds = 0 if stage == "pair" else cadence - 1
    plan = frame_plan(
        2 if stage == "pair" else anchors, final_holds=holds, multiplier=cadence
    )
    count = cadence + 1 if stage == "pair" else FRAME_COUNT
    require(
        len(plan) == len(manifest["output_frames"]) == count
        and manifest["final_holds"] == holds,
        f"RIFE frame count or tail differs: {case}/{stage}",
    )
    inventory(target / "frames", range(count))
    for i, (expected, row) in enumerate(zip(plan, manifest["output_frames"])):
        require(
            all(row.get(k) == v for k, v in expected.items())
            and row["index"] == i
            and row["time_seconds"] == i / FPS
            and row["file"] == f"frames/{i:04d}.png",
            f"RIFE output plan differs: {case}/{stage}/{i}",
        )
        frame = target / row["file"]
        require(sha(frame) == row["sha256"], f"RIFE frame checksum differs: {frame}")
        pixels(frame, SIZE)
        if expected["kind"] != "interpolation":
            require(
                sha(root / f"anchors/{expected['source_index'] * CADENCE:04d}.png")
                == row["sha256"],
                f"RIFE anchor/hold not byte-identical: {case}/{i}",
            )
    require(
        sha(target / "preview.mp4") == manifest["video_sha256"],
        "RIFE video checksum differs",
    )
    if stage == "full":
        pair = check_rife(
            root, "pair", size=size, fps=fps, cadence=cadence, frame_count=frame_count
        )
        require(
            Path(manifest["validated_pair"]).resolve()
            == (section / "pair/manifest.json").resolve(),
            "Validated pair path differs",
        )
        require(
            all(manifest[k] == pair[k] for k in ("sources", "settings", "provenance")),
            "Pair/full sources, settings or provenance differ",
        )
    return manifest
