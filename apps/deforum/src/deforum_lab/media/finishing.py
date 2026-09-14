"""Prepare saved paintings for the existing pinned RIFE runtime."""

import subprocess

from PIL import Image, ImageDraw

from deforum_lab.records import copy_verified, read, require


def prepare(root, fps=24):
    cadence = read(root / "config.json").get("cadence", 12)
    files = sorted((root / "anchors").glob("*.png"))
    require(
        bool(files)
        and [int(p.stem) for p in files]
        == list(range(0, len(files) * cadence, cadence)),
        "Expected contiguous painting anchors",
    )
    target = root / f"section-{len(files):03d}"
    source = target / "sources"
    for i, path in enumerate(files):
        copy_verified(path, source / f"{i:04d}.png")
    for start in range(0, len(files), 8):
        page = files[start : start + 8]
        board = Image.new("RGB", (1024, 370 * ((len(page) + 1) // 2)), "#171717")
        draw = ImageDraw.Draw(board)
        for i, path in enumerate(page):
            x, y = i % 2 * 512, i // 2 * 370
            with Image.open(path) as im:
                im.thumbnail((512, 341))
                board.paste(im, (x, y + 25))
            draw.text(
                (x + 10, y + 6),
                f"{root.name} | continuation {int(path.stem) / fps:.1f}s",
                fill="white",
            )
        board.save(target / f"paintings-{start // 8 + 1:02d}.jpg")
    return target, source, files


def finish_paintings(paths, root, stage, fps=24):
    require(stage in ("prepare", "pair", "full"), "Unknown finishing stage")
    target, source, files = prepare(root, fps)
    if stage == "prepare":
        return
    cadence = read(root / "config.json").get("cadence", 12)
    require(
        fps % cadence == 0, "This finishing adapter expects an integer painting rate"
    )
    args = [
        str(paths.rife_python),
        str(paths.rife_script),
        str(source),
        str(target / ("pair" if stage == "pair" else "rife")),
        "--source-frames",
        str(len(files)),
        "--source-fps",
        str(fps // cadence),
        "--multiplier",
        str(cadence),
    ]
    args += (
        ["--pair-only"]
        if stage == "pair"
        else ["--validated-pair", str(target / "pair/manifest.json")]
    )
    subprocess.run(args, check=True)
