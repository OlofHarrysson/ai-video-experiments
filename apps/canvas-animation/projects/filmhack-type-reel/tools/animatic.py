# /// script
# dependencies = ["pillow", "numpy"]
# ///
"""Real-speed comprehension animatic for three Filmhack Reel openings (placeholder look).

usage: animatic.py <out_dir>
"""
import sys, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS, BPM = 540, 960, 30, 140
BEAT = 60 / BPM
SUP = "/System/Library/Fonts/Supplemental/"
FONTS = [  # (path, fill, stroke)
    (SUP + "Impact.ttf", "#ff2d7a", None),
    (SUP + "Georgia Bold Italic.ttf", "#ffd400", None),
    (SUP + "Arial Black.ttf", "#000000", "#19e3ff"),
    (SUP + "Courier New Bold.ttf", "#ffffff", None),
    (SUP + "Arial Black.ttf", "#ff3a2a", None),
    (SUP + "Impact.ttf", "#000000", "#ffd400"),
    (SUP + "Georgia Bold.ttf", "#19e3ff", None),
    ("/System/Library/Fonts/HelveticaNeue.ttc", "#ffffff", None),
]
QUIET = ImageFont.truetype(SUP + "Georgia Italic.ttf", 34)
LABEL = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
ROLES = ["DIRECTOR", "CAMERA", "SOUND", "EDITOR", "WRITER", "DESIGNER", "PRODUCER"]

def C(t, beats, **o): return dict(t=t, d=beats, **o)
SEQ = {
    "A · doubt vs answer": [
        C("make a film in 48 hours?", 1.5, q=1), C("YES.", 1, z=230), C("i've never touched AI", 1, q=1),
        C("NO AI\nEXPERIENCE\nNEEDED", 2, z=110), C("i don't have a crew", 1, q=1), C("CREWS\nFORM\nFRIDAY", 2, z=140),
        C("48 hours isn't enough", 1, q=1), C("CONSTRAINTS\nBEAT\nTALENT", 2, z=88), C("and if it's a mess?", 1, q=1),
        C("IT STILL\nPREMIERES", 2, z=110), C("maybe next ye—", 0.7, q=1), C("NOV 13–15\nBABELSBERG", 2, z=100, flip=1),
        C("APPLY BY\nOCT 24", 2.5, z=120)],
    "B · this film needs a ___": [
        C("", 2, slot="DIRECTOR"), C("", 2, slot="SOUND"), C("", 2, slot="EDITOR"), C("IT HAS\n48 HOURS.", 2, z=120),
        C("AND A\nPREMIERE.", 2, z=120, flip=1), C("IT NEEDS\nYOU.", 2, z=140), C("APPLY BY\nOCT 24", 2.5, z=120)],
    "C · action!": [
        C("ROLLING!", 1, z=120), C("SPEED!", 1, z=140), C("MARK!", 1, z=150), C("", 0.5, flash=1),
        C("quiet on set.", 2, q=1), C("ACTION!", 2, z=150, flip=1), C("48 HOURS", 1, z=120),
        C("100\nFILMMAKERS", 1, z=95), C("ONE\nCINEMA", 1, z=130), C("CUT!", 1, z=210),
        C("SUNDAY,\nIT PLAYS.", 2, z=105), C("APPLY BY\nOCT 24", 2.5, z=120)],
}

def fit_text(d, text, style, size):
    path, fill, stroke = FONTS[style]
    while True:
        f = ImageFont.truetype(path, size)
        box = d.multiline_textbbox((0, 0), text, font=f, align="center", spacing=size * 0.02, stroke_width=4 if stroke else 0)
        if box[2] - box[0] <= W - 48 or size < 20: return f, fill, stroke, box
        size = int(size * 0.92)

def big(d, text, style, size):
    f, fill, stroke, box = fit_text(d, text, style, size)
    x = (W - (box[2] - box[0])) / 2 - box[0]; y = (H - (box[3] - box[1])) / 2 - box[1]
    d.multiline_text((x, y), text, font=f, fill=fill, align="center", spacing=size * 0.02,
                     stroke_width=4 if stroke else 0, stroke_fill=stroke)

frames, hits, t_global = [], [], 0.0
def emit(img):
    frames.append(img)

for name, seq in SEQ.items():
    for _ in range(int(1.4 * FPS)):  # slate
        im = Image.new("RGB", (W, H), "#111"); d = ImageDraw.Draw(im)
        d.text((W / 2, H / 2), name, font=ImageFont.truetype(SUP + "Arial Black.ttf", 30), fill="#ddd", anchor="mm")
        d.text((W / 2, H / 2 + 44), "timing animatic · placeholder look", font=LABEL, fill="#777", anchor="mm")
        emit(im)
    for i, card in enumerate(seq):
        n = round(card["d"] * BEAT * FPS)
        if not card.get("q") and not card.get("flash"): hits.append(len(frames) / FPS)
        for k in range(n):
            lt = k / FPS
            im = Image.new("RGB", (W, H), "#fff" if card.get("flash") else "#000"); d = ImageDraw.Draw(im)
            if card.get("q"):
                d.text((48, H - 330), card["t"], font=QUIET, fill="#8a8a8a")
            elif card.get("slot"):
                spin = lt < BEAT * 1.25
                r = ROLES[int(lt / 0.09) % len(ROLES)] if spin else card["slot"]
                st = int(lt / 0.09) % len(FONTS) if spin else (i * 3) % len(FONTS)
                d.multiline_text((W / 2, H / 2 - 150), "THIS FILM\nNEEDS A", font=ImageFont.truetype(
                    "/System/Library/Fonts/HelveticaNeue.ttc", 52, index=1), fill="#fff", anchor="ma", align="center")
                f, fill, stroke, box = fit_text(d, r, st, 110)
                d.text((W / 2, H / 2 + 90), r, font=f, fill=fill, anchor="mm", stroke_width=4 if stroke else 0, stroke_fill=stroke)
            elif not card.get("flash"):
                st = int(lt / (BEAT / 2)) % len(FONTS) if card.get("flip") else (i * 3 + 1) % len(FONTS)
                big(d, card["t"], st, card["z"])
            d.text((16, 14), name, font=LABEL, fill="#555")
            emit(im)
    for _ in range(int(0.5 * FPS)): emit(Image.new("RGB", (W, H), "#000"))

for j, im in enumerate(frames): im.save(OUT / f"f{j:05d}.png")
dur = len(frames) / FPS

# --- audio: kick on beats, hat on offbeats, noise hit on answer cards (beat grid restarts per section)
sr = 44100; a = np.zeros(int(dur * sr) + sr)
def kick(t0):
    n = int(0.25 * sr); tt = np.arange(n) / sr
    s = np.sin(2 * np.pi * (50 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)
    i = int(t0 * sr); a[i:i + n] += 0.8 * s[: len(a) - i]
def noise(t0, amp, decay, n_s):
    n = int(n_s * sr); s = np.random.default_rng(int(t0 * 1000)).standard_normal(n) * np.exp(-np.arange(n) / sr * decay)
    i = int(t0 * sr); a[i:i + n] += amp * s[: len(a) - i]
t, sections = 0.0, []
for name, seq in SEQ.items():
    t += 1.4; start = t; t += sum(c["d"] for c in seq) * BEAT; sections.append((start, t)); t += 0.5
for s0, s1 in sections:
    b = s0
    while b < s1 - 1e-6:
        kick(b); noise(b + BEAT / 2, 0.08, 60, 0.05); b += BEAT
for h in hits: noise(h, 0.35, 9, 0.35)
a = a / np.max(np.abs(a)) * 0.8
with wave.open(str(OUT / "audio.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(OUT / "f%05d.png"), "-i", str(OUT / "audio.wav"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-shortest", str(OUT / "filmhack-openings-animatic.mp4")], check=True)
print(f"{len(frames)} frames, {dur:.1f}s ->", OUT / "filmhack-openings-animatic.mp4")
