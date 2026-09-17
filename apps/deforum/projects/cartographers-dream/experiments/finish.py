"""Finish The Cartographer’s Dream at 4.5x source speed and 24 fps.

Every painting is retained at round(source_frame / 4.5), with two- or three-frame
intervals. Run pair, inspect its preview, then full. The default tail
holds the last painting; tail creates an optional moving alternative for inspection.
Check verifies an existing full delivery and its moving tail if present.
--through-frame selects a source painting boundary; omission includes all paintings.
Existing outputs are immutable. --version selects the source export version.
"""

import argparse
import copy
import subprocess
from bisect import bisect_right
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import numpy as np
from PIL import Image

from deforum_lab.image import warps
from deforum_lab.records import copy_verified, read, require, save, sha

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
APP = HERE.parents[2]
EXPORTS = PROJECT / "exports"
FPS = 24
SOURCE_INTERVAL = 12
SPEED = 4.5
RIFE_PYTHON = APP / "work/rife-session/.venv/bin/python"
RIFE_SCRIPT = APP / "interpolate.py"


def pixels(path):
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))


def inventory(path):
    with Image.open(path) as image:
        image.load()
        require(image.mode == "RGB", f"Expected RGB painting: {path}")
        require(all(n % 2 == 0 for n in image.size), "Expected even dimensions")
        size = list(image.size)
    return {"sha256": sha(path), "size": size, "mtime_ns": path.stat().st_mtime_ns}


def verify_lineage(source, config, last, seen=None):
    """Verify inherited paintings and resolve the motion following the last one."""
    source = source.resolve()
    seen = set() if seen is None else seen
    require(source not in seen, "Cyclic painting prefix")
    seen.add(source)
    if "prefix_root" not in config:
        return source, config
    prefix = (APP / config["prefix_root"]).resolve()
    require(prefix.is_relative_to(EXPORTS.resolve()), "Prefix must belong to this project")
    through = config["prefix_through"]
    require(through in config["painting_frames"], "Prefix boundary differs")
    rows = read(source / "prefix.json")
    require(
        [row["frame"] for row in rows]
        == [frame for frame in config["painting_frames"] if frame <= through],
        "Prefix inventory differs",
    )
    for row in rows:
        if row["frame"] > last:
            break
        original = prefix / f"anchors/{row['frame']:04d}.png"
        require(
            (APP / row["source"]).resolve() == original
            and sha(source / f"anchors/{row['frame']:04d}.png")
            == row["sha256"]
            == sha(original),
            "Inherited painting differs",
        )
    parent = read(prefix / "config.json")
    owner, motion = verify_lineage(prefix, parent, min(last, through), seen)
    return (owner, motion) if last < through else (source, config)


def prepare(case, through, create, version="v001"):
    require(
        case not in ("", ".", "..") and Path(case).name == case, "Expected case name"
    )
    require(version in ("v001", "v002"), "Expected export version v001 or v002")
    source = EXPORTS / version / case
    config = read(source / "config.json")
    require(config["case"] == case, "Frozen config case differs")
    positions = config["painting_frames"]
    require(
        positions
        and positions[0] == 0
        and all(type(frame) is int and frame >= 0 for frame in positions)
        and all(b - a == SOURCE_INTERVAL for a, b in pairwise(positions)),
        "Expected painting anchors at 0, 12, 24, ...",
    )
    require(config["cadence"] == SOURCE_INTERVAL, "Source cadence differs")
    require(
        positions[-1] + SOURCE_INTERVAL == round(config["duration"] * FPS),
        "Source duration differs",
    )
    last = positions[-1] if through is None else through
    require(last in positions, "--through-frame must be a source painting boundary")
    selected = [frame for frame in positions if frame <= last]
    require(len(selected) >= 2, "Finishing requires at least two paintings")
    motion_source, motion_config = verify_lineage(source, config, last)
    root = source / ("faster" if through is None else f"through-{through:04d}")
    delivery = [round(frame / SPEED) for frame in selected]
    frame_count = round((last + SOURCE_INTERVAL) / SPEED)
    require(
        all(b - a in (2, 3) for a, b in pairwise(delivery))
        and frame_count > delivery[-1],
        "Expected distinct painting anchors and a complete final interval",
    )
    rows = []
    for index, frame in enumerate(selected):
        original = source / f"anchors/{frame:04d}.png"
        rows.append(
            {
                "frame": frame,
                "file": str(original.relative_to(APP)),
                "copy": f"sources/{index:04d}.png",
                **inventory(original),
            }
        )
    require(
        all(row["size"] == rows[0]["size"] for row in rows), "Painting sizes differ"
    )
    timing = {
        "source_case": case,
        "source_config_sha256": sha(source / "config.json"),
        "source_start_frame": 0,
        "source_anchor_frames": selected,
        "delivery_anchor_frames": delivery,
        "speed_multiplier": SPEED,
        "fps": FPS,
        "frame_count": frame_count,
        "new_diffusion_jobs": 0,
        "sources": rows,
        "finisher_sha256": sha(Path(__file__)),
        "interpolator_sha256": sha(RIFE_SCRIPT),
        "warp_sha256": sha(Path(warps.__file__)),
    }
    if motion_source != source.resolve():
        timing["tail_config_file"] = str((motion_source / "config.json").relative_to(APP))
        timing["tail_config_sha256"] = sha(motion_source / "config.json")
    if not create:
        # Producer identity is immutable provenance, not the current verifier version.
        timing["finisher_sha256"] = read(root / "retiming.json")["finisher_sha256"]
    if create:
        save(root / "anchor-frames.json", delivery)
    require(read(root / "anchor-frames.json") == delivery, "Anchor timing differs")
    timing["anchor_frames_sha256"] = sha(root / "anchor-frames.json")
    if create:
        save(root / "retiming.json", timing)
        for row in rows:
            copy_verified(APP / row["file"], root / row["copy"])
    require(read(root / "retiming.json") == timing, "Frozen finishing inputs differ")
    expected_names = {f"{i:04d}.png" for i in range(len(rows))}
    require(
        {p.name for p in (root / "sources").glob("*.png")} == expected_names,
        "Finishing source inventory differs",
    )
    for row in rows:
        require(sha(root / row["copy"]) == row["sha256"], "Copied painting differs")
    return source, root, motion_config, timing


def verify_video(target, count, size):
    import json

    video = target / "preview.mp4"
    probe = json.loads(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_streams",
                "-of",
                "json",
                str(video),
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    stream = probe["streams"][0]
    require(int(stream["nb_read_frames"]) == count, "Encoded frame count differs")
    require(Fraction(stream["avg_frame_rate"]) == FPS, "Encoded frame rate differs")
    require(
        abs(float(stream["duration"]) - count / FPS) < 0.00001,
        "Encoded duration differs",
    )
    require([stream["width"], stream["height"]] == size, "Encoded size differs")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(video), "-f", "null", "-"],
        check=True,
    )


def verify(root, timing, config, mode, manifest=None):
    target = root / mode
    record = read(target / "manifest.json") if manifest is None else manifest
    require(record["status"] == "complete", "Finishing did not complete")
    require(sha(target / "preview.mp4") == record["video_sha256"], "Video hash differs")
    positions = timing["delivery_anchor_frames"]
    pair = mode == "pair"
    moving = mode == "rife-moving-tail"
    count = positions[1] + 1 if pair else timing["frame_count"]
    last = positions[1] if pair else positions[-1]
    tail_frames = 0 if pair else count - last - 1
    settings = record["settings"]
    require(record["mode"] == ("first_pair" if pair else "full"), "RIFE mode differs")
    require(
        settings["output_fps"] == FPS
        and settings["anchor_frames"] == positions
        and settings["frame_count"] == timing["frame_count"]
        and settings["pair_lengths"] == [b - a for a, b in pairwise(positions)]
        and settings["scale"] == 1,
        "RIFE timing or scale differs",
    )
    require(
        record["provenance"]["model"] == "RIFE 4.25"
        and record["provenance"]["runner_sha256"] == timing["interpolator_sha256"],
        "RIFE implementation differs",
    )
    sources = [
        {"file": str((root / row["copy"]).resolve()), **inventory(root / row["copy"])}
        for row in timing["sources"]
    ]
    require(record["sources"] == sources, "RIFE sources changed")
    rows = record["output_frames"]
    require(
        [row["index"] for row in rows] == list(range(count)), "Frame indices differ"
    )
    require(
        record["final_holds"] == (0 if moving else tail_frames),
        "Final hold count differs",
    )
    if moving:
        require(record["final_warps"] == tail_frames, "Tail length differs")
        require(
            record["tail_recipe"]
            == {
                "source_frame": timing["source_anchor_frames"][-1],
                "delivery_anchor_frame": last,
                "speed_multiplier": SPEED,
                "config_sha256": timing.get(
                    "tail_config_sha256", timing["source_config_sha256"]
                ),
                "warp_sha256": timing["warp_sha256"],
            },
            "Tail recipe differs",
        )
        require(
            record["retiming_sha256"] == sha(root / "retiming.json"),
            "Tail timing hash differs",
        )
        require(
            record["parent_manifest_sha256"] == sha(root / "rife/manifest.json"),
            "Tail parent receipt differs",
        )
        require(
            record["parent_video_sha256"] == sha(root / "rife/preview.mp4"),
            "Tail parent video differs",
        )
        last_image = pixels(root / timing["sources"][-1]["copy"])
    for row in rows:
        index = row["index"]
        require(row["file"] == f"frames/{index:04d}.png", "Frame filename differs")
        path = target / row["file"]
        require(sha(path) == row["sha256"], f"Frame hash differs: {index}")
        require(row["time_seconds"] == index / FPS, "Frame time differs")
        source_index = bisect_right(positions, index) - 1
        if index <= last and positions[source_index] == index:
            require(
                row["kind"] == "anchor"
                and row["source_index"] == source_index
                and row["sha256"] == timing["sources"][source_index]["sha256"],
                "Original painting was not retained",
            )
        elif index < last:
            left = source_index
            interval = positions[left + 1] - positions[left]
            require(
                row["kind"] == "interpolation"
                and row["source_pair"] == [left, left + 1]
                and row["timestep"]
                == f"{index - positions[left]}/{interval}",
                "Interpolation timing differs",
            )
        elif moving:
            seconds = (timing["source_anchor_frames"][-1] + (index - last) * SPEED) / FPS
            require(
                row["kind"] == "warp"
                and row["source_index"] == len(positions) - 1
                and row["source_time_seconds"] == seconds,
                "Tail source time differs",
            )
            expected = warps.warp_at_time(
                last_image,
                timing["source_anchor_frames"][-1] / FPS,
                seconds,
                config["phrases"],
            )
            require(np.array_equal(pixels(path), expected), "Tail warp pixels differ")
        else:
            require(
                row["kind"] == "final_hold"
                and row["source_index"] == len(positions) - 1
                and row["sha256"] == timing["sources"][-1]["sha256"],
                "Final hold differs",
            )
        if moving and index <= last:
            require(
                sha(path) == sha(root / "rife" / row["file"]), "Pre-tail frame changed"
            )
    verify_video(target, count, timing["sources"][0]["size"])
    save(
        target / "delivery-check.json",
        {
            "verified": True,
            "frames": count,
            "fps": FPS,
            "paintings": 2 if pair else len(positions),
            "final_holds": 0 if moving else tail_frames,
            "final_warps": tail_frames if moving else 0,
            "tail_changed_pixels": (
                bool(np.any(pixels(target / rows[-1]["file"]) != last_image))
                if moving
                else None
            ),
            "video_sha256": record["video_sha256"],
            "retiming_sha256": sha(root / "retiming.json"),
            "anchor_frames_sha256": timing["anchor_frames_sha256"],
        },
    )
    return record


def interpolate(root, timing, config, stage):
    target = root / ("pair" if stage == "pair" else "rife")
    require(not target.exists(), f"Preserve previous finishing output: {target}")
    require(RIFE_PYTHON.is_file(), f"Missing local RIFE Python: {RIFE_PYTHON}")
    if stage == "full":
        verify(root, timing, config, "pair")
    command = [
        str(RIFE_PYTHON),
        str(RIFE_SCRIPT),
        str(root / "sources"),
        str(target),
        "--source-frames",
        str(len(timing["sources"])),
        "--anchor-frames",
        str(root / "anchor-frames.json"),
        "--output-fps",
        str(FPS),
        "--frame-count",
        str(timing["frame_count"]),
    ]
    command += (
        ["--pair-only"]
        if stage == "pair"
        else ["--validated-pair", str(root / "pair/manifest.json")]
    )
    save(
        root / f"{stage}-command.json",
        {
            "command": command,
            "cwd": str(APP),
            "retiming_sha256": sha(root / "retiming.json"),
        },
    )
    subprocess.run(command, cwd=APP, check=True)
    verify(root, timing, config, target.name)


def tail(root, timing, config):
    target = root / "rife-moving-tail"
    require(not target.exists(), f"Preserve previous tail output: {target}")
    original = verify(root, timing, config, "rife")
    record = copy.deepcopy(original)
    last = timing["delivery_anchor_frames"][-1]
    last_source = timing["source_anchor_frames"][-1]
    tail_frames = timing["frame_count"] - last - 1
    last_image = pixels(root / timing["sources"][-1]["copy"])
    record.update(
        status="finishing",
        parent_video_sha256=original["video_sha256"],
        parent_manifest_sha256=sha(root / "rife/manifest.json"),
        retiming_sha256=sha(root / "retiming.json"),
        final_holds=0,
        final_warps=tail_frames,
        tail_recipe={
            "source_frame": last_source,
            "delivery_anchor_frame": last,
            "speed_multiplier": SPEED,
            "config_sha256": timing.get(
                "tail_config_sha256", timing["source_config_sha256"]
            ),
            "warp_sha256": timing["warp_sha256"],
        },
    )
    for row in record["output_frames"]:
        path = target / row["file"]
        if row["index"] <= last:
            copy_verified(root / "rife" / row["file"], path)
        else:
            seconds = (last_source + (row["index"] - last) * SPEED) / FPS
            rgb = warps.warp_at_time(
                last_image, last_source / FPS, seconds, config["phrases"]
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgb).save(path)
            row.update(
                kind="warp",
                source_index=len(timing["sources"]) - 1,
                source_time_seconds=seconds,
                sha256=sha(path),
            )
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-n",
        "-framerate",
        str(FPS),
        "-start_number",
        "0",
        "-i",
        str(target / "frames/%04d.png"),
        "-frames:v",
        str(timing["frame_count"]),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movie_timescale",
        str(FPS),
        "-movflags",
        "+faststart",
        str(target / "preview.mp4"),
    ]
    record["encode_command"] = command
    save(target / "pending-manifest.json", record)
    subprocess.run(command, check=True)
    record.update(status="complete", video_sha256=sha(target / "preview.mp4"))
    verify(root, timing, config, target.name, record)
    save(target / "manifest.json", record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("stage", choices=["pair", "full", "check", "tail"])
    parser.add_argument("--version", choices=["v001", "v002"], default="v001")
    parser.add_argument(
        "--through-frame",
        type=int,
        help="Last source painting frame; default: all paintings",
    )
    args = parser.parse_args()
    _, root, config, timing = prepare(
        args.case, args.through_frame, args.stage in ("pair", "full"), args.version
    )
    if args.stage in ("pair", "full"):
        interpolate(root, timing, config, args.stage)
    elif args.stage == "tail":
        tail(root, timing, config)
    else:
        verify(root, timing, config, "rife")
        if (root / "rife-moving-tail").exists():
            verify(root, timing, config, "rife-moving-tail")
    prepare(args.case, args.through_frame, False, args.version)
    print(f"Verified {args.stage}: {root}", flush=True)


if __name__ == "__main__":
    main()
