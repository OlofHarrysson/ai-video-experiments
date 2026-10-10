# /// script
# dependencies = ["librosa", "numpy", "matplotlib"]
# ///
"""Spectrogram + loudness + onsets for a window, with observed card changes marked.

usage: sound.py <video> <start> <dur> <out.png> <title> [comma-separated change times]
"""
import sys, subprocess, numpy as np, librosa, librosa.display
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

video, start, dur, out, title = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
marks = [float(x) for x in sys.argv[6].split(",")] if len(sys.argv) > 6 and sys.argv[6] else []
sr = 22050
y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", str(dur),
    "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=2048, hop_length=256)), ref=np.max)
rms = librosa.feature.rms(y=y, hop_length=256)[0]; t_rms = librosa.times_like(rms, sr=sr, hop_length=256) + start
_, beats = librosa.beat.beat_track(y=y, sr=sr, units="time"); beats += start
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=256, units="time") + start
# low (kick/bass) vs high (hats/vocal sibilance) band energy
f = librosa.fft_frequencies(sr=sr, n_fft=2048); P = 10 ** (S / 10)
low = 10 * np.log10(P[f < 150].mean(0) + 1e-12); mid = 10 * np.log10(P[(f > 300) & (f < 3000)].mean(0) + 1e-12)

fig, ax = plt.subplots(3, 1, figsize=(18, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1.2, 1]})
librosa.display.specshow(S, sr=sr, hop_length=256, x_axis="time", y_axis="log", ax=ax[0], cmap="magma",
                         x_coords=librosa.times_like(S[0], sr=sr, hop_length=256) + start)
ax[0].set_title(title); ax[0].set_ylim(40, 11000)
ax[1].plot(t_rms, 20 * np.log10(rms + 1e-9), lw=0.8, label="RMS dB")
tt = librosa.times_like(low, sr=sr, hop_length=256) + start
ax[1].plot(tt, low - low.max(), lw=0.6, alpha=.7, label="<150Hz"); ax[1].plot(tt, mid - mid.max(), lw=0.6, alpha=.7, label="300-3k")
ax[1].legend(loc="lower right", fontsize=7); ax[1].set_ylim(-60, 0)
ax[2].vlines(beats, 0, 1, color="tab:blue", lw=1, label="beats")
ax[2].vlines(onsets, 0, .5, color="tab:orange", lw=.8, label="onsets")
ax[2].vlines(marks, .5, 1, color="tab:green", lw=1.5, label="card changes (observed)")
ax[2].legend(loc="upper right", fontsize=7, ncol=3); ax[2].set_yticks([])
for a in ax:
    a.set_xlim(start, start + dur)
ticks = np.arange(np.ceil(start), start + dur, 1.0)
ax[2].set_xticks(ticks); ax[2].set_xticklabels([f"{int(t//60):02d}:{t%60:04.1f}" for t in ticks], fontsize=7)
plt.tight_layout(); plt.savefig(out, dpi=80)
iv = np.median(np.diff(beats))
print(f"{title}: tempo≈{60/iv:.1f} bpm, beat {iv:.3f}s")
if marks:
    d_on = [min(abs(onsets - m)) for m in marks]; d_b = [min(abs(beats - m)) for m in marks]
    print("change→nearest onset (ms):", " ".join(f"{d*1000:.0f}" for d in d_on))
    print("change→nearest beat  (ms):", " ".join(f"{d*1000:.0f}" for d in d_b))
