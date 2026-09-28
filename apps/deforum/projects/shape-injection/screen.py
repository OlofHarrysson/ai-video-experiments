"""Make input/output comparison sheets from preserved experiment artifacts."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
WIDTH, HEIGHT = 512, 288


def sheet(items, destination, columns=2):
    canvas = Image.new(
        "RGB",
        (WIDTH * columns, (HEIGHT + 36) * ((len(items) + columns - 1) // columns)),
        "#18202a",
    )
    draw = ImageDraw.Draw(canvas)
    for i, (path, label) in enumerate(items):
        x, y = i % columns * WIDTH, i // columns * (HEIGHT + 36)
        canvas.paste(Image.open(path).convert("RGB").resize((WIDTH, HEIGHT)), (x, y))
        draw.text((x + 8, y + HEIGHT + 8), label, fill="white")
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)
    print(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["probes", "sequence"])
    parser.add_argument("--name")
    args = parser.parse_args()
    if args.stage == "probes":
        cases = sorted((ROOT / "exports/probes").glob("*/case.json"))
        for page in range(0, len(cases), 6):
            items = []
            for case in cases[page : page + 6]:
                name = json.loads(case.read_text())["name"]
                items += [
                    (case.parent / "injected.png", name + " INPUT"),
                    (case.parent / "output.png", name + " OUTPUT"),
                ]
            sheet(items, ROOT / f"exports/probe-sheet-{page // 6 + 1}.jpg")
    else:
        folder = ROOT / "exports/sequences" / args.name
        frames = sorted((folder / "frames").glob("*.png"))
        indices = sorted({round(i * (len(frames) - 1) / 7) for i in range(8)})
        sheet(
            [(frames[i], f"{args.name}: painting {i}") for i in indices],
            folder / "contact-sheet.jpg",
            4,
        )
