# /// script
# dependencies = ["transformers==5.19.0", "torch==2.14.1", "torchvision==0.29.1", "pillow", "numpy"]
# ///
"""Per-letter masks for generated lettering with SAM 2.1, prompted by estimated letter boxes.

usage: segment_letters.py <image> <out_dir> <line text> <y0 frac> <y1 frac> [<line text> <y0> <y1> ...]

Writes labels.png (letter index per pixel, 0 = background), letter-NN.png alpha masks, overlay.png and letters.json.
Letter boxes come from the image's own column gaps, split by approximate relative glyph widths where letters touch.
"""
import json, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image, ImageDraw
from transformers import Sam2Model, Sam2Processor

MODEL = "facebook/sam2.1-hiera-base-plus"
WIDTH = {"C": 1.0, "R": 1.0, "E": .9, "W": 1.35, "S": .95, "F": .85, "O": 1.1, "M": 1.25, "I": .45, "D": 1.05, "A": 1.1, "Y": 1.0}

img_path, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
specs = [(sys.argv[i], float(sys.argv[i + 1]), float(sys.argv[i + 2])) for i in range(3, len(sys.argv), 3)]
image = Image.open(img_path).convert("RGB"); W, H = image.size
rgb = np.asarray(image).astype(np.float32) / 255
fg = (.3 * rgb[..., 0] + .59 * rgb[..., 1] + .11 * rgb[..., 2]) > .1

letters = []
for text, f0, f1 in specs:
    y0, y1 = int(f0 * H), int(f1 * H)
    cols = fg[y0:y1].sum(0) > 3
    chunks, start = [], None
    for x, on in enumerate(list(cols) + [False]):
        if on and start is None: start = x
        if not on and start is not None:
            if x - start > 10: chunks.append([start, x])
            start = None
    x0, x1 = chunks[0][0], chunks[-1][1]
    widths = [WIDTH[c] for c in text]; total = sum(widths); acc = 0
    owner = []
    for w in widths:  # which chunk holds each letter's estimated centre
        cx = x0 + (acc + w / 2) / total * (x1 - x0); acc += w
        owner.append(min(range(len(chunks)), key=lambda k: 0 if chunks[k][0] <= cx <= chunks[k][1] else min(abs(cx - chunks[k][0]), abs(cx - chunks[k][1]))))
    for k, (c0, c1) in enumerate(chunks):
        idx = [i for i, o in enumerate(owner) if o == k]
        if not idx: continue
        sub = sum(widths[i] for i in idx); a = c0
        for i in idx:
            b = a + widths[i] / sub * (c1 - c0)
            ys = np.where(fg[y0:y1, int(a):max(int(a) + 1, int(b))].any(1))[0]
            letters.append({"char": text[i], "box": [int(a), y0 + int(ys.min()), int(b), y0 + int(ys.max())]})
            a = b

device = "mps" if torch.backends.mps.is_available() else "cpu"
proc = Sam2Processor.from_pretrained(MODEL); model = Sam2Model.from_pretrained(MODEL).to(device).eval()
boxes = [[l["box"] for l in letters]]
points = [[[[(l["box"][0] + l["box"][2]) / 2, (l["box"][1] + l["box"][3]) / 2]] for l in letters]]
labels = [[[1] for _ in letters]]
inputs = proc(images=image, input_boxes=boxes, input_points=points, input_labels=labels, return_tensors="pt").to(device)
with torch.no_grad():
    res = model(**inputs, multimask_output=False)
logits = proc.post_process_masks(res.pred_masks.cpu(), inputs["original_sizes"].cpu(), binarize=False)[0][:, 0].numpy()

# Each foreground pixel goes to the most confident letter; pixels no letter claims stay unlabelled.
best = logits.argmax(0); conf = logits.max(0)
label = np.where(fg & (conf > 0), best + 1, 0).astype(np.uint8)
# Foreground above the first line is the loose-ribbon layer; other leftovers join the nearest letter.
RIBBONS = len(letters) + 1
top = int(specs[0][1] * H) - 4
label[:top][fg[:top] & (label[:top] == 0)] = RIBBONS
for _ in range(600):
    todo = fg & (label == 0)
    if not todo.any(): break
    grown = label.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        shifted = np.roll(np.roll(label, dy, 0), dx, 1)
        take = todo & (grown == 0) & (shifted > 0) & (shifted != RIBBONS)
        grown[take] = shifted[take]
    label = grown
letters.append({"char": "ribbons", "box": [0, 0, W, top]})
Image.fromarray(label).save(out / "labels.png")
palette = np.array([[0, 0, 0]] + [[int(v) for v in np.random.default_rng(i).integers(60, 255, 3)] for i in range(len(letters))], np.uint8)
overlay = Image.fromarray((rgb * 255 * .35 + palette[label] * .65).astype(np.uint8)); d = ImageDraw.Draw(overlay)
for i, l in enumerate(letters):
    m = label == i + 1
    Image.fromarray((m * 255).astype(np.uint8)).save(out / f"letter-{i:02d}.png")
    l["pixels"] = int(m.sum()); d.rectangle(l["box"], outline=(255, 255, 255), width=2); d.text((l["box"][0] + 4, l["box"][1] + 2), f"{i} {l['char']}", fill=(255, 255, 255))
overlay.save(out / "overlay.png")
json.dump({"image": img_path, "model": MODEL, "size": [W, H], "letters": letters, "unclaimed_fg": int((fg & (label == 0)).sum()), "fg": int(fg.sum())}, open(out / "letters.json", "w"), indent=1)
print(len(letters), "letters;", "unclaimed foreground", round((fg & (label == 0)).sum() / fg.sum() * 100, 1), "%")
