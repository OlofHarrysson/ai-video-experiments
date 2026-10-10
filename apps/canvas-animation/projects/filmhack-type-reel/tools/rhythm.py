# /// script
# dependencies = ["librosa", "numpy"]
# ///
"""Relate visual change (ffmpeg scdet scores) to the audio's beats and onsets.

usage: rhythm.py <video> <scdet.txt> <start_s> <dur_s> <fps> <cut_threshold>
"""
import sys, subprocess, numpy as np, librosa

video, scdet, start, dur, fps, thr = sys.argv[1:7]
start, dur, fps, thr = float(start), float(dur), float(fps), float(thr)

# --- visual: per-frame scene score
scores, t = [], None
for line in open(scdet):
    if "pts_time:" in line:
        t = float(line.split("pts_time:")[1].split()[0])
    elif "lavfi.scd.score=" in line and t is not None:
        scores.append((start + t, float(line.split("=")[1])))
scores = np.array(scores)
cuts = scores[scores[:, 1] >= thr][:, 0]
gaps = np.diff(cuts)
print(f"frames={len(scores)} cuts(score>={thr})={len(cuts)}  per-second={len(cuts)/dur:.2f}")
print("cut gap frames: median %.1f  p25 %.1f  p75 %.1f  max %.1f" % tuple(
    np.percentile(gaps * fps, [50, 25, 75, 100])))

# --- audio
wav = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", str(dur),
                      "-ac", "1", "-ar", "22050", "-f", "f32le", "-"], capture_output=True).stdout
y = np.frombuffer(wav, dtype=np.float32); sr = 22050
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
beats = beats + start
onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=False) + start
rms = librosa.feature.rms(y=y, hop_length=sr // 4)[0]
print(f"tempo≈{float(np.atleast_1d(tempo)[0]):.1f} bpm  beats={len(beats)}  onsets={len(onsets)}")
beat_iv = np.median(np.diff(beats)) if len(beats) > 1 else 0
print(f"beat interval {beat_iv:.3f}s = {beat_iv*fps:.1f} frames; 8th = {beat_iv*fps/2:.1f} frames")

def near(xs, ref, tol):
    return np.array([np.min(np.abs(ref - x)) <= tol for x in xs]) if len(ref) else np.zeros(len(xs), bool)
tol = 1.5 / fps
print(f"cuts within ±1.5 frames of a beat: {near(cuts, beats, tol).mean()*100:.0f}%   "
      f"of an onset: {near(cuts, onsets, tol).mean()*100:.0f}%")
# chance baseline: random times
rng = np.random.default_rng(0); rnd = rng.uniform(start, start + dur, 2000)
print(f"  chance baseline beat {near(rnd, beats, tol).mean()*100:.0f}%  onset {near(rnd, onsets, tol).mean()*100:.0f}%")

# per-second table: cuts, onsets, loudness
print("\nsec    cuts onsets  rms(dB)   bar")
for s in range(int(dur)):
    a, b = start + s, start + s + 1
    c = int(((cuts >= a) & (cuts < b)).sum()); o = int(((onsets >= a) & (onsets < b)).sum())
    r = 20 * np.log10(np.mean(rms[s * 4:(s + 1) * 4]) + 1e-9)
    m, sec = divmod(a, 60)
    print(f"{int(m):02d}:{sec:04.1f}  {c:3d}  {o:4d}   {r:6.1f}   " + "#" * c + "." * max(0, o - c))
print("\nbeats:", " ".join(f"{b:.2f}" for b in beats))
print("\ncuts:", " ".join(f"{c:.2f}" for c in cuts))
