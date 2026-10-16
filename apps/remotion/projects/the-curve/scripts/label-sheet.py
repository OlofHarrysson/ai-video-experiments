# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Labelled 2×2 contact sheet: uv run --script scripts/label-sheet.py OUT.png "Title" IMG:LABEL ..."""
import sys
from PIL import Image, ImageDraw, ImageFont

out, title, *items = sys.argv[1:]
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
W, H = 960, 540
cols = 2
rows = (len(items) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows + 60), "black")
d = ImageDraw.Draw(sheet)
d.text((20, 14), title, font=font, fill="white")
for i, item in enumerate(items):
    path, label = item.split(":", 1)
    img = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = (i % cols) * W, 60 + (i // cols) * H
    sheet.paste(img, (x, y))
    tw = d.textlength(label, font=small)
    d.rectangle([x + 12, y + 12, x + 12 + tw + 24, y + 52], fill=(0, 0, 0))
    d.text((x + 24, y + 18), label, font=small, fill="white")
sheet.save(out)
print(out)
