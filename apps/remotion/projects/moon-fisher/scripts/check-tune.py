# /// script
# requires-python = ">=3.11"
# dependencies = ["librosa", "numpy", "soundfile"]
# ///
"""Pitch-track a dry stem and compare it with the written notes.

    uv run --script scripts/check-tune.py renders/score/clarinet.wav
    uv run --script scripts/check-tune.py renders/score/glock.wav glock
"""
import sys

import librosa
import numpy as np

BAR, EIGHTH = 2.0, 2.0 / 6
# (bar, eighth, note, eighths) as written in src/audio/score.ts
CLARINET = [
    (2, 0, "A4", 3), (2, 3, "F#5", 2), (2, 5, "E5", 1),
    (3, 0, "D5", 2), (3, 2, "E5", 1), (3, 3, "F#5", 3),
    (4, 0, "B4", 3), (4, 3, "G5", 2), (4, 5, "F#5", 1),
    (5, 0, "E5", 2), (5, 2, "F#5", 1), (5, 3, "E5", 3),
    (6, 0, "A4", 3), (6, 3, "F#5", 2), (6, 5, "E5", 1),
    (7, 0, "D5", 2), (7, 2, "E5", 1), (7, 3, "F#5", 2), (7, 5, "A5", 1),
    (8, 0, "G5", 2), (8, 2, "F#5", 1), (8, 3, "E5", 2), (8, 5, "C#5", 1),
    (9, 0, "D5", 6),
    (18, 0, "A4", 3), (18, 3, "F5", 2), (18, 5, "E5", 1),
    (19, 0, "D5", 2), (19, 2, "E5", 1), (19, 3, "F5", 3),
    (20, 0, "E5", 3), (20, 3, "D5", 3),
    (23, 0, "G4", 3), (23, 3, "E5", 3),
    (24, 0, "A4", 3), (24, 3, "F#5", 3),
    (25, 0, "B4", 3), (25, 3, "G#5", 2), (25, 5, "F#5", 1),
    (26, 0, "E5", 2), (26, 2, "F#5", 1), (26, 3, "G#5", 2), (26, 5, "B5", 1),
    (27, 0, "A5", 2), (27, 2, "G#5", 1), (27, 3, "F#5", 2), (27, 5, "D#5", 1),
    (28, 0, "E5", 6),
    (29, 0, "B4", 3), (29, 3, "G#5", 3),
    (30, 0, "F#5", 2), (30, 2, "E5", 4),
]
GLOCK = [
    (1, 3, "A6", 3), (9, 3, "D7", 3),
    (13, 3, "D6", 1), (13, 4, "F#6", 1), (13, 5, "C#7", 1),
    (14, 0, "A5", 3), (14, 3, "F#6", 2), (14, 5, "E6", 1),
    (15, 0, "D6", 2), (15, 2, "E6", 1), (15, 3, "F#6", 3),
    (16, 0, "B5", 3), (16, 3, "G6", 2), (16, 5, "F#6", 1),
    (17, 0, "E6", 2), (17, 2, "F#6", 1), (17, 3, "E6", 3),
    (18, 0, "A5", 3), (19, 0, "D6", 3), (20, 0, "E6", 3),
    (24, 3, "E6", 1), (24, 4, "G#6", 1), (24, 5, "B6", 1),
    (25, 0, "B5", 3), (25, 3, "G#6", 2), (25, 5, "F#6", 1),
    (26, 0, "E6", 2), (26, 2, "F#6", 1), (26, 3, "G#6", 2), (26, 5, "B6", 1),
    (27, 0, "A6", 2), (27, 2, "G#6", 1),
    (27, 3, "E6", 0.5), (27, 3.5, "G#6", 0.5), (27, 4, "B6", 1),
    (30, 3, "B6", 3),
]
PART = sys.argv[2] if len(sys.argv) > 2 else "clarinet"
WRITTEN = {"clarinet": CLARINET, "glock": GLOCK}[PART]
RANGE = {"clarinet": (150, 1400), "glock": (700, 4200)}[PART]

y, sr = librosa.load(sys.argv[1], sr=22050 if PART == "clarinet" else 44100, mono=True)
f0, voiced, _ = librosa.pyin(y, fmin=RANGE[0], fmax=RANGE[1], sr=sr, frame_length=2048, hop_length=128)
times = librosa.times_like(f0, sr=sr, hop_length=128)
bad = 0
for bar, eighth, note, length in WRITTEN:
    t0 = (bar - 1) * BAR + eighth * EIGHTH
    t1 = t0 + length * EIGHTH
    mid = (times > t0 + 0.2 * (t1 - t0)) & (times < t0 + 0.8 * (t1 - t0)) & voiced
    want = librosa.note_to_midi(note)
    if not mid.any():
        print(f"bar {bar:2d}.{eighth} {note:4s} unvoiced"); bad += 1; continue
    got = float(np.median(librosa.hz_to_midi(f0[mid])))
    err = 100 * (got - want)
    flag = "" if abs(err) < 50 else "  <-- WRONG"
    bad += bool(flag)
    print(f"bar {bar:2d}.{eighth} {note:4s} heard {librosa.midi_to_note(round(got)):4s} {err:+6.0f} cents{flag}")
print(f"{len(WRITTEN) - bad}/{len(WRITTEN)} notes match")
