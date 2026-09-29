# /// script
# requires-python = ">=3.11"
# dependencies = ["librosa", "numpy", "soundfile"]
# ///
"""Pitch-track a dry single-instrument stem and compare it with the notes
the score scheduled for that instrument (renders/score/notes.json, written
by every score render).

    npm run score -- --stem clarinet
    uv run --script scripts/check-tune.py clarinet
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PART = sys.argv[1]
RANGE = {"clarinet": (140, 1400), "violin": (180, 2400), "piano": (60, 4200)}[PART]
# Chords can't be checked by a single-pitch tracker: only notes that sound
# alone, starting after the previous note of this instrument has ended.
notes = sorted(
    (n for n in json.loads((ROOT / "renders/score/notes.json").read_text()) if n["instrument"] == PART),
    key=lambda n: n["time"],
)
WRITTEN = [
    n for i, n in enumerate(notes)
    if all(abs(m["time"] - n["time"]) > 0.02 for m in notes[max(0, i - 3): i + 4] if m is not n)
]

y, sr = librosa.load(ROOT / f"renders/score/{PART}.wav", sr=44100, mono=True)
f0, voiced, _ = librosa.pyin(y, fmin=RANGE[0], fmax=RANGE[1], sr=sr, frame_length=2048, hop_length=128)
times = librosa.times_like(f0, sr=sr, hop_length=128)
bad = 0
for n in WRITTEN:
    note = n["note"]
    t0, t1 = n["time"], n["time"] + min(n["duration"], 1.2)
    mid = (times > t0 + 0.2 * (t1 - t0)) & (times < t0 + 0.8 * (t1 - t0)) & voiced
    want = librosa.note_to_midi(note)
    if not mid.any():
        print(f"{t0:6.2f}s {note:4s} unvoiced"); bad += 1; continue
    got = float(np.median(librosa.hz_to_midi(f0[mid])))
    err = 100 * (got - want)
    flag = "" if abs(err) < 50 else "  <-- WRONG"
    bad += bool(flag)
    print(f"{t0:6.2f}s {note:4s} heard {librosa.midi_to_note(round(got)):4s} {err:+6.0f} cents{flag}")
print(f"{len(WRITTEN) - bad}/{len(WRITTEN)} notes match")
