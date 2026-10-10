# /// script
# dependencies = ["numpy", "librosa"]
# ///
"""Classify frame-to-frame changes on dark typographic footage.

replace  = lit-pixel layout changes (low IoU of bright masks)
flicker  = layout kept, brightness/colour changes a lot
hold     = little change
usage: changes.py <video> <start> <dur> <fps>
"""
import sys, subprocess, numpy as np, librosa

video, start, dur, fps = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
W, H = 192, 96
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", str(dur),
                      "-vf", f"scale={W}:{H}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255
lum = fr.mean(axis=3)
mask = lum > 0.18
events = []
for i in range(1, len(fr)):
    a, b = mask[i - 1], mask[i]
    union = (a | b).sum(); iou = (a & b).sum() / union if union else 1.0
    mad = np.abs(fr[i] - fr[i - 1]).mean()
    lit = b.mean()
    if union < 20: kind = "dark"
    elif iou < 0.45: kind = "REPLACE"
    elif mad > 0.035: kind = "flicker"
    else: kind = "hold"
    events.append((start + i / fps, kind, iou, mad, lit))

kinds = [e[1] for e in events]
rep = np.array([e[0] for e in events if e[1] == "REPLACE"])
print(f"{len(fr)} frames  replace={len(rep)}  flicker={kinds.count('flicker')}  hold={kinds.count('hold')}  dark={kinds.count('dark')}")
gaps = np.diff(rep) * fps
if len(gaps):
    print("frames between replacements: median %.0f  p25 %.0f  p75 %.0f" % tuple(np.percentile(gaps, [50, 25, 75])))
    hist = np.bincount(np.clip(np.round(gaps).astype(int), 0, 30))
    print("gap histogram (frames:count):", " ".join(f"{k}:{v}" for k, v in enumerate(hist) if v))

wav = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", str(dur),
                      "-ac", "1", "-ar", "22050", "-f", "f32le", "-"], capture_output=True).stdout
y = np.frombuffer(wav, np.float32)
_, beats = librosa.beat.beat_track(y=y, sr=22050, units="time"); beats = beats + start
iv = np.median(np.diff(beats)); grid8 = np.concatenate([beats, beats[:-1] + np.diff(beats) / 2])
tol = 1.0 / fps
on8 = np.mean([np.min(np.abs(grid8 - r)) <= tol for r in rep]) if len(rep) else 0
rnd = np.random.default_rng(1).uniform(start, start + dur, 3000)
base = np.mean([np.min(np.abs(grid8 - r)) <= tol for r in rnd])
print(f"beat {iv:.3f}s ({iv*fps:.1f} fr). replacements within ±1 frame of the 8th-note grid: {on8*100:.0f}% (chance {base*100:.0f}%)")

# a compact strip: one char per frame, 24 per row
sym = {"REPLACE": "R", "flicker": "f", "hold": ".", "dark": " "}
print("\nper-frame strip (R=replace f=flicker .=hold ' '=dark), | marks a beat")
row, t0 = "", start
bset = set(np.round((beats - start) * fps).astype(int))
for i, e in enumerate(events, start=1):
    row += ("|" if i in bset else "") + sym[e[1]]
    if i % int(round(fps)) == 0:
        m, s = divmod(t0, 60); print(f"{int(m):02d}:{s:05.2f} {row}"); row, t0 = "", start + i / fps
if row: m, s = divmod(t0, 60); print(f"{int(m):02d}:{s:05.2f} {row}")
