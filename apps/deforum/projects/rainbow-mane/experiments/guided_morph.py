"""Paint the approved authored morph with recurrent Krea and explicit geometry."""

import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from deforum_lab.image.landmarks import warp_landmarks
from deforum_lab.infrastructure.pod import PodClient
from deforum_lab.records import copy_verified, read, require, save, sha
from deforum_lab.rendering.graphs import repaint_graph
from deforum_lab.rendering.verification import validate_execution

APP = Path(__file__).resolve().parents[3]
PROJECT = APP / "projects/rainbow-mane"
GUIDE = PROJECT / "exports/profile-morph-v002"
OUT = PROJECT / "exports/guided-morph-v001"
STYLE = (
    "A cinematic mixed-media punk comic-book animation frame. One character only, "
    "strict right-facing side profile, only one visible eye. Preserve the exact head "
    "silhouette, position of the eye, nose and rainbow hair shown in the input. "
    "Chalk-white sculpted forms with violet halftone-dot shadow, expressive ink-black "
    "eye, thick rough brush-ink contours, cyan offset rim light, gritty crosshatching, "
    "screen-printed paper grain and layered misregistered colors. Keep the eye readable. "
    "The upright crest develops into a mane, with red orange yellow green cyan violet "
    "in that order. Magenta and purple dimensional background, acid-yellow shards and "
    "cyan brush marks at the edges, quieter behind the white silhouette. Fixed camera, "
    "same close-up composition, head and crest fully inside the frame. No lettering. "
)
STAGES = [
    (
        0,
        "A round white cartoon person's head with a small nose, round cheek, small ear and an upright rainbow punk mohawk. A short white neck and shoulders below.",
    ),
    (
        0.12,
        "The same round white cartoon face begins to lengthen forward: a slightly longer nose and jaw, with one expressive eye and a small rising ear. The rainbow crest begins extending down the back of the neck.",
    ),
    (
        0.32,
        "One continuous white face midway between a cartoon person and a pony. The nose and jaw form a short rounded muzzle. The same visible eye persists, the ear rises toward the crown and the rainbow crest stretches down the neck.",
    ),
    (
        0.62,
        "A white cartoon pony head in side profile, one expressive eye, a lengthening rounded muzzle and pointed ears. The connected rainbow mane extends along the back of the curved white neck.",
    ),
    (
        0.88,
        "A white horse head in strict right-facing side profile, one expressive eye, a long rounded equine muzzle, two pointed ears and a rainbow mane flowing down the back of its curved white neck. Only the head and neck bust is visible.",
    ),
]


def prompt(progress):
    return STYLE + next(text for start, text in reversed(STAGES) if progress >= start)


def curve_samples(points, per_curve=3):
    p = np.asarray(points, float)
    result = []
    for i in range(1, len(p), 3):
        a, b, c, d = p[i - 1 : i + 3]
        for t in np.linspace(0, 1, per_curve, endpoint=False):
            result.append(
                (1 - t) ** 3 * a
                + 3 * (1 - t) ** 2 * t * b
                + 3 * (1 - t) * t * t * c
                + t**3 * d
            )
    return result


def handles(row):
    p = curve_samples(row["outline_control_points"])
    p += curve_samples(row["ear_control_points"], 4)
    p += row["mane_roots"] + row["mane_tips"] + [row["eye"], row["nostril"]]
    # Fixed outer pins anchor the distant background, not the silhouette edge.
    for y in [0, 120, 240, 360, 480, 600, 719]:
        for x in [0, 160, 1040, 1279]:
            p.append([x, y])
    for x in [320, 480, 640, 800, 960]:
        p.append([x, 0])
    return np.asarray(p)


def image(path):
    return np.asarray(Image.open(path).convert("RGB"))


def prepare(previous, before, after, guide, alpha, root, frame):
    warped, stats = warp_landmarks(image(previous), handles(before), handles(after))
    require(
        stats["folded_pixel_fraction"] == 0,
        f"Authored field folds at frame {frame}: {stats}",
    )
    target = image(guide)
    foreground = (
        np.max(np.abs(target.astype(float) - [48, 43, 64]), axis=2) > 35
    ).astype(np.float32)
    foreground[687:] = 0
    foreground = cv2.dilate(foreground, np.ones((17, 17), np.uint8))
    weight = cv2.GaussianBlur(foreground, (0, 0), 8)[:, :, None] * alpha
    blended = (
        np.clip(warped * (1 - weight) + target * weight, 0, 255)
        .round()
        .astype(np.uint8)
    )
    for folder, pixels in [("warped", warped), ("inputs", blended)]:
        (root / folder).mkdir(exist_ok=True, parents=True)
        Image.fromarray(pixels).save(root / folder / f"{frame:04d}.png")
    return root / "inputs" / f"{frame:04d}.png", stats


def submit(client, case, frame, source, noise, seed, text, lineage):
    g = repaint_graph(
        text, seed, [s * noise / 0.6 for s in [0.6, 0.512844085693, 0.310901075602, 0]]
    )
    g["11"]["inputs"]["filename_prefix"] = f"rainbow-guided/{case}/{frame:04d}"
    run = client.submit_once(
        OUT, f"rainbow-guided-{case}-{frame:04d}", g, source=source, lineage=lineage
    )
    executed, history = read(run / "workflow.executed.json"), read(run / "history.json")
    validate_execution(
        g,
        executed,
        read(run / "upload.json"),
        history,
        read(run / "submit-response.json"),
        read(run / "submission.json"),
        lineage.get("parent_sha256"),
        sha(source),
    )
    require(
        history["status"]["status_str"] == "success" and history["status"]["completed"],
        "Incomplete generation",
    )
    require(history["prompt"][2] == executed, "Executed graph mismatch")
    require(
        executed["9"]["inputs"]["latent_image"] == ["24", 0],
        "Previous-image initialization missing",
    )
    require(executed["24"]["inputs"]["pixels"] == ["20", 0], "Image encoding missing")
    target = OUT / case / "anchors" / f"{frame:04d}.png"
    copy_verified(run / "frames/0000.png", target)
    require(Image.open(target).size == (1280, 720), "Wrong image dimensions")
    png_graph = json.loads(Image.open(target).info["prompt"])
    changed = png_graph["20"].pop("is_changed", None)
    require(
        changed is None or changed == [sha(source)], "PNG input fingerprint differs"
    )
    require(png_graph == executed, "PNG graph differs")
    return {
        "frame": frame,
        "source_sha256": sha(source),
        "output_sha256": sha(target),
        "run": str(run.relative_to(OUT)),
        "noise": noise,
        "seed": seed,
        **lineage,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["preflight", "opening", "sequence"])
    p.add_argument("--deployment", type=Path)
    p.add_argument("--case", required=True)
    p.add_argument("--noise", type=float, default=0.55)
    p.add_argument("--guide-alpha", type=float, default=0.12)
    p.add_argument("--source", type=Path)
    p.add_argument("--through", type=int, default=93)
    args = p.parse_args()
    require(0 < args.noise <= 1 and 0 <= args.guide_alpha <= 1, "Bad strengths")
    require(
        0 <= args.through <= 93 and args.through % 3 == 0,
        "Expected a 24fps frame divisible by 3",
    )
    landmarks = read(GUIDE / "landmarks.json")
    root = OUT / args.case
    root.mkdir(parents=True, exist_ok=True)
    config = {
        "case": args.case,
        "stage": args.stage,
        "noise": args.noise,
        "guide_alpha": args.guide_alpha,
        "fps": 24,
        "painting_cadence": 3,
        "guide_sha256": sha(GUIDE / "manifest.json"),
        "guide_landmarks_sha256": sha(GUIDE / "landmarks.json"),
        "source": str(args.source.resolve()) if args.source else None,
        "source_sha256": sha(args.source) if args.source else None,
        "method": "inverse thin-plate landmark warp, local guide blend, previous-image partial-noise repaint",
        "reference_conditioning": None,
        "style_prompt": STYLE,
        "stages": STAGES,
    }
    if (root / "config.json").exists():
        require(
            read(root / "config.json") == json.loads(json.dumps(config)),
            "Case config changed",
        )
    else:
        save(root / "config.json", config)
    if args.stage == "preflight":
        source = GUIDE / "frames/0000.png"
        rows = []
        for f in range(3, 94, 3):
            target, stats = prepare(
                source,
                landmarks[f - 3],
                landmarks[f],
                GUIDE / f"frames/{f:04d}.png",
                args.guide_alpha,
                root,
                f,
            )
            source = target
            rows.append({"frame": f, **stats})
        save(root / "fields.json", rows)
        print(
            "Fields checked:",
            len(rows),
            "minimum Jacobian:",
            min(r["min_jacobian"] for r in rows),
        )
        return
    require(args.deployment is not None, "Deployment required")
    client = PodClient.from_path(args.deployment)
    if args.stage == "opening":
        source = GUIDE / "frames/0000.png"
        row = submit(
            client,
            args.case,
            0,
            source,
            args.noise,
            10012611,
            prompt(0),
            {"role": "opening painted from approved guide"},
        )
        save(root / "jobs.json", [row])
        print(root / "anchors/0000.png")
        return
    require(args.source is not None, "Selected painted opening required")
    copy_verified(args.source, root / "anchors/0000.png")
    rows = []
    for f in range(3, args.through + 1, 3):
        parent = root / "anchors" / f"{f - 3:04d}.png"
        source, stats = prepare(
            parent,
            landmarks[f - 3],
            landmarks[f],
            GUIDE / f"frames/{f:04d}.png",
            args.guide_alpha,
            root,
            f,
        )
        row = submit(
            client,
            args.case,
            f,
            source,
            args.noise,
            10012620 + f,
            prompt(landmarks[f]["face_progress"]),
            {
                "parent_frame": f - 3,
                "parent_sha256": sha(parent),
                "guide_frame": f,
                "guide_sha256": sha(GUIDE / f"frames/{f:04d}.png"),
                "field": stats,
            },
        )
        rows.append(row)
        save(root / "receipts" / f"{f:04d}.json", row)
        print(f"{args.case}: {f}/93", flush=True)
    save(root / f"jobs-through-{args.through:04d}.json", rows)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-pattern_type",
            "glob",
            "-framerate",
            "8",
            "-i",
            str(root / "anchors/*.png"),
            "-vf",
            "fps=24",
            "-c:v",
            "libx264",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(root / f"through-{args.through:04d}-raw.mp4"),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
