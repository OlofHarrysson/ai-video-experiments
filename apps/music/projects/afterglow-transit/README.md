# Afterglow Transit

2026-10-17. A new 126 BPM melodic deep-house/trance study requested by Olof, separate from Undercurrent. Approximately 65 seconds, with a new score, bass phrase and original procedural sound palette. Human taste verdict pending.

[Open the shared player](http://localhost:3046/) or [play the complete mix](exports/player-v002/afterglow-transit.wav). Nine synchronized parts can be muted or isolated: kick, bass, clap, hats, wood percussion, warm chords, lead melody, arpeggio and air swells. The player and standalone WAV use the same sum of stems. Earlier songs and both revisions remain preserved.

## Musical intent

The harmonic loop is Dm9 → B-flat major 9 → F major 9 → Cadd9, with each harmony lasting two bars. Close upper voicings move above a changing bass root. The lead begins as a sparse question, develops through related phrases, and reaches higher notes during the final return. A quieter arpeggio adds movement behind it. The chord samples have a beat-synchronous volume dip to leave room for the kick, including during the exposed breakdown.

| Time | Section |
| --- | --- |
| 0:00–0:08 | Chords and groove; bass enters after two bars |
| 0:08–0:23 | Sparse theme becomes a fuller melodic phrase |
| 0:23–0:30 | Full texture and a transition swell |
| 0:30–0:38 | Drums and bass drop out; exposed harmony, then melody |
| 0:38–0:46 | Half-time kick, then a clap build; bass held back |
| 0:46–0:57 | Full kick/bass return with brighter lead and two phrase variations |
| 0:57–1:05 | Release and final D-minor resolution with tails |

[make_palette.py](make_palette.py) synthesizes detuned harmonic pads/leads, an FM arpeggio, a pitched kick, filtered-noise hats/clap, wood percussion and air. Synthesis runs at 96 kHz before downsampling to 48 kHz PCM24; deterministic seed and sample hashes are in [palette provenance](references/palette-v001.json). No reference audio or artist sample is used.

## Screening and revision

V001's complete master and nine stems rendered successfully without PCM rail contacts. A 53-second master excerpt was sent to `google/gemini-4-argon` via OpenRouter/Google after verifying the live catalog. The high-reasoning response completed with finish reason `stop`, reporting $0.027. The prompt is [preserved](review-prompt.txt); receipts are local in `../../work/afterglow-transit-20261017/review/`.

The model recognized the broad roles and breakdown, and raised a concern that the rhythm returned before the main lift. It missed some written melodic variation and conflated the staggered kick/bass entries, so its timestamps and claims of exact repetition were not accepted as ground truth. V002 makes the intended main return explicit: bass/full kick wait until bar 25, a half-time kick and two-bar clap build carry the preceding passage, and air swells are quieter. V002 received local screening, not another model review.

[Final evidence](evidence.json) records the published mix measurements, source/output hashes, common 0.85 gain and final 150 ms fade. [Sound Lab report](exports/sound-lab-v002/report.md) compares the theme and return plus isolated lead/chords. The separately rendered wet master is preserved; randomized effect responses mean exact wet master/stem reconstruction is not assumed. The downloadable mix is made from the actual player stems so those two listening paths agree.

Technical screening cannot establish taste, emotional impact or club quality. The next useful evidence is Olof's reaction to the complete piece and its isolated parts.

The final playback measures **−15.90 LUFS / −2.60 dBTP**, with no overload. A sample check verifies the player-stem sum against the WAV within 4.9e−8, bass silence through the build, and a zero final sample. 39 Python tests, six engine tests, Ruff and desktop/mobile browser checks pass. Publishing a different song exposed a hardcoded player title; the heading and browser title now use the manifest, with live assertions. No visual redesign or renderer change was needed.

## Reproduce

From `apps/music`, with the local sample assets restored:

```sh
uv run --locked python music.py render-project projects/afterglow-transit/project.json --revision v002 --out NEW_RENDER
uv run --locked python sound_lab.py projects/afterglow-transit/sound-lab.json --out NEW_INSPECTION
```

`project-v001.json` preserves the first revision's stem partition. `compose.py` records how the initial explicit score was expanded; `source/v002.strudel` is the authoritative revised score. `make_palette.py` creates its versioned asset directory only when absent. `publish.py` refuses to replace an output bundle; select new input/output version constants for a new publication. Media remains local/ignored; recipes, generators, sources and evidence are tracked.
