# Latch

A 132 BPM, thirty-second contender for the club-detail sprint. It retains Undertow's interlocking F bass and 909 foundation, adding original noise-friction percussion and a moving, saturated bass response. Four modules separate drums, bass, breath and edits; setup owns tempo and score constants. The current challenger is `renders/v006/master/render.wav`; it has not received a human listening verdict.

## Decisions

| Revision | Experiment | Evidence and limit |
| --- | --- | --- |
| v001 | Woody resonator and full low-end break | A model called the wood toy-like and the break an interruption. Its claim that all percussion disappeared was false; the pacing concern remained plausible. |
| v002 | Remove wood, darken breath, keep half-rate middle pulse, expose burred bass | Preserved first refinement. |
| v003 | Shared short ambience on breath/burr | Anonymous review called the real change identical. This gives no reliable preference; small source changes are not proof of audible improvement. |
| v004 | Continuous kick, four-bar pattern shifts, individually arranged friction calls and bass responses | Completed master and four stems. A turn interruption left a separate partial run; the complete run is `renders/v004-complete`. The structure offers a contrast to the other candidates' exposure/return. |
| v005 | Print a shared short stereo room before saturating the original shuck/burr samples | Completed master and four stems; clean raw PCM. The objects now carry their room within their texture. Bass/percussion sometimes meet in unison accents; this is not a rule that every attack is separated. Preserved as the preceding challenger. |
| v006 | Recurring two-bar friction/burr identity; two bass phrases return, with development through articulation and two small timing changes | Completed master and four stems. Actual exporter traces show the opening timing cell returns five times; v005 had seven different two-bar cells. This establishes recurrence, not musical superiority. Current challenger. |

V006 is −16.38 LUFS / −2.40 dBTP with zero PCM rail samples and approximately 0.039 dB mono RMS loss. Its master and four stems are aligned at 1,439,999 frames; their hashes and ending levels are recorded in `motif-evidence.json`. V005 remains −16.59 LUFS / −2.16 dBTP with zero PCM rail samples. Its master loses approximately 0.04 dB RMS when folded to mono. The breath stem gains roughly 5.5 LU relative to the globally attenuated v004 baseline; this establishes a substantial signal change, not perceived quality. A preserved anonymous matched v004/v005 pair is in the sprint's ignored audition folder.

The room-before-saturation experiment was informed by [Gesloten Cirkel's direct Ableton interview](https://www.ableton.com/en/blog/gesloten-cirkel-free-tools-and-tips-for-spicing-up-sounds/). He discusses driving reverb tails into saturation as part of an instrument's character. Our implementation uses an original deterministic short stereo impulse response and a tanh waveshaper; it does not reproduce his devices or claim his sound. All musical material remains original apart from the retained drum library.

## The returning gesture

Two friction attacks recur at the same positions while the burred low response alternates between an earlier and a later answer. The first eight bars keep the bass rhythm familiar; bars 8–11 lengthen the bass and open the burr articulation. The original colour and rolling bass return in bars 12–13. A missing friction hit in bar 6 and a short pickup in bar 11 create small departures from that identity. Drum and ending modules are unchanged from v005.

The new `render --trace-events` option was dogfooded on the v005/v006 foreground layers. `motif-evidence.json` records three unique two-bar timing variants in v006 versus seven in v005. That count is evidence of this specific recurrence choice, not a quality score. Raw trace receipts and a loudness-matched 28-second comparison remain local under `reviews/`; no new audio-model call was made. V006 replaces v005 as the challenger on compositional grounds, without claiming it surpasses the sprint's selected pair.

## Reproduce

From `apps/music`, with its locked environment and renderer installed:

```sh
uv run --locked python projects/latch/make_palette.py
uv run --locked python projects/latch/make_room_objects.py
uv run --locked python music.py assemble projects/latch/assembly-v006.json --out outputs/latch-assembly-new
uv run --locked python music.py render-project outputs/latch-assembly-new/project.json --revision v006 --out outputs/latch-render-new
```

Generators require fresh asset destinations and refuse to overwrite preserved originals. On this working copy the assets already exist. Run `uv run --locked python projects/latch/rebuild_audit.py` for a safe fresh-directory reconstruction check instead. [Evidence](rebuild-evidence.json) verifies all six generated assets and complete palette receipts against the retained files. The drum library must also be restored from its [provenance](../practical-dogfood/drum-sources.json).

The renderer writes 1,439,999 frames at 48 kHz for 16.5 cycles at 132 BPM: 29.999979 seconds, one sample short of 30 seconds because of floating-point rounding. Original renders and all four stems remain local/ignored. Wet renders can differ slightly between runs; source/sample hashes and technical checks are the reproducibility boundary, not exact wet master bytes.

`make_palette.py`, `palette.json`, `make_room_objects.py` and `room-objects.json` preserve deterministic synthesis/processing and sample hashes. No third-party music or voice is sampled. Human listening remains the taste judgment.
