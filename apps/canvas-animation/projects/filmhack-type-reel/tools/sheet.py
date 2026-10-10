# /// script
# dependencies = ["pillow"]
# ///
"""Extract frames from a video window and tile them into labelled contact sheets.

usage: sheet.py <video> <out_dir> <start_s> <end_s> <fps|all> <cols> <thumb_w> [per_sheet]
"""
import subprocess, sys, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

video, out_dir, start, end, fps, cols, thumb_w = sys.argv[1:8]
per_sheet = int(sys.argv[8]) if len(sys.argv) > 8 else 10_000
start, end, cols, thumb_w = float(start), float(end), int(cols), int(thumb_w)
out = Path(out_dir); frames = out / "frames"; frames.mkdir(parents=True, exist_ok=True)
for f in frames.glob("*.png"): f.unlink()

vf = "showinfo" if fps == "all" else f"fps={fps},showinfo"
cmd = ["ffmpeg", "-hide_banner", "-ss", f"{start}", "-i", video, "-t", f"{end-start}",
       "-vf", vf, "-vsync", "0", str(frames / "f%05d.png")]
log = subprocess.run(cmd, capture_output=True, text=True).stderr
pts = []
for line in log.splitlines():
    if "pts_time:" in line:
        pts.append(float(line.split("pts_time:")[1].split()[0]))
files = sorted(frames.glob("*.png"))
times = [start + p for p in pts][: len(files)]
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
first = Image.open(files[0]); th = round(first.height * thumb_w / first.width)
manifest = []
for s in range(math.ceil(len(files) / per_sheet)):
    chunk = list(zip(files, times))[s * per_sheet:(s + 1) * per_sheet]
    rows = math.ceil(len(chunk) / cols)
    sheet = Image.new("RGB", (cols * (thumb_w + 4), rows * (th + 22)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (f, t) in enumerate(chunk):
        x, y = (i % cols) * (thumb_w + 4), (i // cols) * (th + 22)
        sheet.paste(Image.open(f).resize((thumb_w, th)), (x, y + 20))
        m, sec = divmod(t, 60)
        d.text((x + 2, y + 2), f"{int(m):02d}:{sec:06.3f}", fill=(255, 220, 0), font=font)
        manifest.append({"file": f.name, "t": round(t, 3)})
    sheet.save(out / f"sheet-{s:02d}.jpg", quality=88)
(out / "manifest.json").write_text(json.dumps(manifest, indent=1))
print(len(files), "frames;", math.ceil(len(files) / per_sheet), "sheets ->", out)
