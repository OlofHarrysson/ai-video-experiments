# /// script
# dependencies = ["pillow", "numpy", "scipy"]
# ///
"""Split a transparent-background generation into parts by connected alpha regions.

usage: segment_layers.py <rgba image> <out_dir> <letters in reading order, e.g. CREWSFORMFRIDAY>

Parts above the first row of letters become separate ribbon layers. Same output format as segment_letters.py.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

img_path, out, chars = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
rgba = np.asarray(Image.open(img_path).convert("RGBA")); H, W = rgba.shape[:2]
solid = rgba[..., 3] > 40
comp, n = ndimage.label(solid, structure=np.ones((3, 3)))
parts = []
for i, sl in enumerate(ndimage.find_objects(comp), start=1):
    size = int((comp[sl] == i).sum())
    if size < 400: continue
    parts.append({"id": i, "box": [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop], "size": size})
# Rows of letters: cluster by vertical centre; the top cluster above the letters holds the loose ribbons.
parts.sort(key=lambda p: (p["box"][1] + p["box"][3]) / 2)
rows, cur = [], [parts[0]]
for p in parts[1:]:
    prev = np.mean([(q["box"][1] + q["box"][3]) / 2 for q in cur])
    if (p["box"][1] + p["box"][3]) / 2 - prev > .05 * H: rows.append(cur); cur = [p]
    else: cur.append(p)
rows.append(cur)
letter_rows = rows[-3:] if len(rows) > 3 else rows
ribbon_parts = [p for r in rows[:-3] for p in r] if len(rows) > 3 else []
ordered = [p for r in letter_rows for p in sorted(r, key=lambda p: p["box"][0])]
if len(ordered) != len(chars):
    print(f"warning: {len(ordered)} letter parts for {len(chars)} characters")

label = np.zeros((H, W), np.uint8); letters = []
for k, p in enumerate(ordered):
    label[comp == p["id"]] = k + 1
    letters.append({"char": chars[k] if k < len(chars) else "?", "box": p["box"], "pixels": p["size"]})
for p in sorted(ribbon_parts, key=lambda p: p["box"][0]):
    label[comp == p["id"]] = len(letters) + 1
    letters.append({"char": "ribbon", "box": p["box"], "pixels": p["size"]})
Image.fromarray(label).save(out / "labels.png")
rgb = rgba[..., :3].astype(np.float32)
palette = np.array([[0, 0, 0]] + [[int(v) for v in np.random.default_rng(i).integers(60, 255, 3)] for i in range(len(letters))], np.uint8)
ov = Image.fromarray((rgb * .35 + palette[label] * .65).astype(np.uint8)); d = ImageDraw.Draw(ov)
for k, l in enumerate(letters):
    d.rectangle(l["box"], outline=(255, 255, 255), width=2); d.text((l["box"][0] + 4, l["box"][1] + 2), f"{k} {l['char']}", fill=(255, 255, 255))
ov.save(out / "overlay.png")
json.dump({"image": img_path, "method": "connected alpha regions", "size": [W, H], "letters": letters}, open(out / "letters.json", "w"), indent=1)
print(len(ordered), "letters,", len(ribbon_parts), "ribbons")
