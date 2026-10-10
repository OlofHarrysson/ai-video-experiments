# /// script
# dependencies = ["pillow"]
# ///
"""Storyboard of selected targets in script order. usage: board.py <targets_dir> <out.jpg>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
T = Path(sys.argv[1])
PANELS = [  # (round/file, label)
    ("round-01/k0-doubt--gemini-nano-banana-2.1.jpg", "1 doubt"),
    ("round-01/k1-yes--gpt-image-2.5-sunburst.png", "2 YES."),
    ("round-01/k2-marquee--gpt-image-2.5-sunburst.png", "3 NO AI EXPERIENCE"),
    ("round-02/k8-come-alone--gpt-image-2.5-sunburst.png", "4 COME ALONE"),
    ("round-01/k3-crew--gpt-image-2.5-sunburst.png", "5 CREWS FORM FRIDAY"),
    ("round-01/k4-constraints--gemini-nano-banana-2.1.jpg", "6 CONSTRAINTS"),
    ("round-02/k5b-rough-cuts-paper--gpt-image-2.5-sunburst.png", "7 ROUGH CUTS"),
    ("round-02/k9-free--gpt-image-2.5-sunburst.png", "8 FREE."),
    ("round-02/k10-full-house--gemini-nano-banana-2.1.jpg", "9 FULL HOUSE"),
    ("round-01/k6-chorus--gpt-image-2.5-sunburst.png", "10 A REAL CREW"),
    ("round-02/k11-dates--gpt-image-2.5-sunburst.png", "11 NOV 13-15"),
    ("round-02/k7b-end--gpt-image-2.5-sunburst.png", "12 APPLY BY OCT 24"),
]
tw, th, cols = 300, 533, 6
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 17)
rows = (len(PANELS) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 40) + 10), (24, 24, 24)); d = ImageDraw.Draw(sheet)
for i, (f, label) in enumerate(PANELS):
    x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 40)
    d.text((x, y + 4), label, fill=(235, 235, 235), font=font)
    sheet.paste(Image.open(T / f).convert("RGB").resize((tw, th)), (x, y + 34))
sheet.save(sys.argv[2], quality=92); print(sys.argv[2], sheet.size)
