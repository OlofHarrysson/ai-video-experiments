# /// script
# dependencies = ["Hershey-Fonts==2.1.0"]
# ///
"""Export single-stroke Hershey skeletons, grouped by letter, for the given lines.

usage: hershey.py <out.json> <font> <line> [<line> ...]
Coordinates are Hershey units with y pointing down; the renderer normalises them.
"""
import json, sys
from HersheyFonts import HersheyFonts

out, font, lines = sys.argv[1], sys.argv[2], sys.argv[3:]
f = HersheyFonts(); f.load_default_font(font)
data = {"font": font, "source": "Hershey fonts (A. V. Hershey, US NBS) via the Hershey-Fonts package", "lines": {}}
for line in lines:
    letters, prev = [], 0
    for i in range(1, len(line) + 1):
        strokes = [list(map(list, s)) for s in f.strokes_for_text(line[:i])]
        letters.append({"char": line[i - 1], "strokes": strokes[prev:]}); prev = len(strokes)
    data["lines"][line] = letters
json.dump(data, open(out, "w"))
print(out, {k: sum(len(l["strokes"]) for l in v) for k, v in data["lines"].items()})
