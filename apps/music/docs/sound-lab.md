# Sound inspection harness

`sound_lab.py` brings the existing waveform/spectrogram, LUFS, true-peak and clipping inspection into a repeatable section comparison. It adds 100 ms RMS/sample-peak timelines, FFmpeg EBU R128 momentary loudness (400 ms), fixed-scale multi-input spectrograms, a two-second waveform close-up, and peak-safe matched copies of complete mixes/references. It runs locally; optional audio-model review remains a separate explicit command through `music.py review`.

## Use

From `apps/music`:

```sh
uv run --locked python sound_lab.py projects/undercurrent/foreground-lab.json --out outputs/foreground-inspection-NEW
uv run --locked python sound_lab.py projects/undercurrent/mix-lab.json --out outputs/mix-inspection-NEW
```

A recipe contains `duration` in seconds and `inputs`, each with `name`, `path` relative to the recipe, optional `start` (default zero), optional `bpm` for bar guides, and `role` (`stem`, `mix` or `reference`). Use actual isolated stems; this is not source separation. Start offsets can differ, so a phone reference and an original sketch can be compared without claiming synchronization. Invalid windows fail rather than being padded; output folders must be new.

The output includes `report.md`, `report.json`, `spectra.png`, `dynamics.png`, `attacks.png`, and per-input excerpts, measurements, CSV and JSON timelines. Source and excerpt hashes identify the exact audio inspected. Failed runs retain a `failed` receipt. The harness never modifies source audio. Crop boundaries retain existing musical effect tails from the rendered source; LUFS integration starts afresh for the selected window.

## Reading it

| View or measure | What it tells us | What it cannot establish |
|---|---|---|
| Spectrogram | Time left to right, frequency low to high; color shows energy. Vertical bursts suggest attacks, horizontal lines reveal tonal harmonics, longer trails show sustain/tails. | Instrument identity, exact perceived sound or whether it is beautiful. Dense and bright is not automatically better. |
| Waveform close-up | How sharply amplitude rises, how it decays, gaps and abrupt edits. Fixed ±1 scale; first two seconds of the chosen passage. | This is not an automatically detected single-note envelope. |
| 100 ms RMS / sample peaks | Physical signal energy over time and brief peaks, including quieter tails. | RMS is not perceived loudness; peaks are not musical impact. |
| Momentary LUFS | Frequency-weighted loudness over 400 ms, showing phrase swells and retreats. First 300 ms are unavailable, not silence. | A perfect model of hearing or taste. |
| Integrated LUFS | Average perceived-loudness estimate over the excerpt, useful for fair comparisons. | A quality score; short excerpts do not describe whole-song dynamics. |
| True peak and rail counts | Reconstructed peak headroom and possible integer saturation. | Full-scale contacts alone do not prove audible distortion. |
| Crest factor | Difference between sample peak and RMS: how peaky versus sustained a passage is. | A universal ideal value or compressor recommendation. |
| Stereo correlation / mono RMS | Possible cancellation when left/right are combined. | Spatial realism or whether width is musically appropriate. |

Spectrograms use the same −100 to −20 dB per frequency-bin color range and logarithmic frequency axis. These are digital measurements, not acoustic sound-pressure levels. Raw plots deliberately retain original levels. Do not judge a louder phone recording against a quieter export solely by color. Channel powers are averaged to avoid hiding opposite-phase audio.

Only inputs marked `mix` or `reference` get level-matched listening copies. All are attenuated to one common LUFS target, lowered further when necessary for at least 1 dB true-peak headroom. There is no compression, peak normalization, boosting or auto-mastering. Stems keep their real mix levels: individually normalizing them would hide balance problems. Silent inputs remain inspectable but cannot be loudness matched.

## Working loop

1. Keep one concrete musical question: for example, does this new pulse grow through the phrase, or does it remain a repeated pluck?
2. Render the isolated part and the full mix. Inspect the same passage in both, alongside a reference when useful.
3. Check alignment, overload, levels, tails, spectral motion and stereo behavior. Investigate suspicious results in source or shorter excerpts.
4. Use `music.py audition` or the harness's matched copies for an audio-input model review when a broad audible distinction needs checking. Save the actual response and uncertainty; follow [listening and calibration](listening.md). Plots and model prose are complementary evidence, not a substitute for hearing.
5. Publish a small comparison in the shared player. Olof judges musical value; use that feedback before extending the arrangement.

Tests cover silence, opposite-phase stereo energy, partial windows, exact excerpts, invalid-window rejection, preservation, loudness startup, matching and true-peak safety with an overloaded float source. The 2026-10-16 foreground study exercises the harness on real rendered stems, complete mixes and the club phone reference. This does not give Codex human hearing.
