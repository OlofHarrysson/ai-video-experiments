# /// script
# dependencies = ["pillow"]
# ///
"""Tile generated targets into labelled comparison sheets: one row per keyframe, one column per model.

usage: compare_targets.py <round_dir> <out.jpg> [thumb_w] [keyframe ids...]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

rd, out = Path(sys.argv[1]), sys.argv[2]
tw = int(sys.argv[3]) if len(sys.argv) > 3 else 300
ids = sys.argv[4:]
files = sorted(p for p in rd.iterdir() if p.suffix in (".png", ".jpg") and "--" in p.name)
kfs = ids or sorted({p.name.split("--")[0] for p in files})
models = sorted({p.stem.split("--")[1].replace(".render", "") for p in files})
th = tw * 16 // 9
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15)
sheet = Image.new("RGB", (len(models) * (tw + 8) + 8, len(kfs) * (th + 30) + 30), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for c, m in enumerate(models):
    d.text((8 + c * (tw + 8), 8), m, fill=(255, 220, 0), font=font)
for r, k in enumerate(kfs):
    for c, m in enumerate(models):
        cand = [p for p in files if p.name.startswith(k + "--" + m)]
        x, y = 8 + c * (tw + 8), 30 + r * (th + 30)
        d.text((x, y), k, fill=(200, 200, 200), font=font)
        if cand:
            im = Image.open(cand[0]).convert("RGB"); im.thumbnail((tw, th))
            sheet.paste(im, (x + (tw - im.width) // 2, y + 22))
sheet.save(out, quality=90)
print(out, sheet.size)
