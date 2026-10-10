# Soft Focus

An original 126 BPM instrumental built after comparing actual DJ_Dave recordings with Chrome After Rain. The production question is whether longer melodic phrases, a sustained harmonic bed and a fuller rhythm move the sound away from the isolated, game-like plucks Olof rejected. Olof rejected this version as still game-like and too much like a children’s song. He wants heavier bass, stronger drums, less melody and an underground techno/club direction; see [Undertow](../undertow/README.md).

## Listen

Selected render: `renders/v001/soft-focus.wav`. The master and five editable stem groups are in `renders/v001/`; the loudness adjustment for the listening copy is saved beside it. All audio remains local and ignored by Git.

The 56-bar arrangement has an opening, a first theme, a stripped middle/build, a return with a changed melodic ending, and an outro. Four additional bars let the effects decay. At 126 BPM:

| Passage | Time | Intended contrast |
| --- | --- | --- |
| Opening | 0:00–0:15 | Filtered harmony and a distant fragment; pulse enters halfway |
| First theme | 0:15–0:46 | Eight-bar lead, offbeat bass, layered percussion |
| Break/build | 0:46–1:01 | Sustained bass and distant phrase; percussion rebuilds |
| Return | 1:01–1:16 | Full rhythm and brighter harmony |
| Last theme | 1:16–1:31 | Changed lead resolution and quiet upper counterline |
| Ending | 1:31–1:47 | Foreground dissolves; rhythm and backing leave in stages |
| Tail | 1:47–1:54 | No new notes; preserved effect decay |

## What the references changed

The [audio study](../dj-dave-reference-study/findings.md) suggested testing transient/sustained contrast and a more expressive foreground. This composition uses held supersaw/triangle phrases, vibrato, varying note accents, complementary chord voicings panned across the stereo field, and quarter-note amplitude modulation on the chord bed. The short sequence is supporting detail. The melody and harmony are newly written; no reference audio is incorporated.

The 16-bar prototype was rendered before arranging the track. Two anonymous, loudness-matched audio comparisons used the same neutral prompt: prototype versus Cycles, and Chrome After Rain versus prototype. The reviewer described the new version as more legato, fuller and more spacious than Chrome, but still markedly different from Cycles' vocal-led foreground. Its claim that the two original tracks share an identical melody is false. It also described the prototype as dry/staccato against Cycles and wet/legato against Chrome, so these relative descriptions are not absolute mix measurements or proof of quality. The lead and chord groups were rendered independently to check that the intended sustained material exists in the actual output.

## Reproduce

From `apps/music`, with the retained sample folders present:

```sh
uv run --locked python music.py render-project projects/soft-focus/project.json \
  --revision v001 --out outputs/soft-focus-v001 --timeout 240
```

The recipe uses the original procedural percussion from [Chrome After Rain](../chrome-after-rain/references/palette.json) and one retained 909 open-hat sample from the [practical study](../practical-dogfood/drum-sources.json). Those studies own the generators/provenance; the render receipt hashes the exact sample library. No stock spoken voice or external music-generation service is used. The renderer and listening tools are unchanged.

Source: [v001](source/v001.strudel). [Recipe](project.json). [Evidence](evidence.json). Paid request receipts are local under `work/soft-focus/`.

## Validation and outcome

The master and five stem groups completed at 48 kHz stereo with identical lengths, finite samples and no clipping. Source and output hashes were verified. The 1:54 listening copy uses a constant +4.8 dB gain, measuring −16.52 LUFS and −1.31 dBTP; the final near-silence is the intentional effect tail. No limiting or hidden processing was added. Nineteen Python tests and Ruff passed; renderer code is unchanged.

Two additional audio-model reviews covered the entire final arrangement in contiguous halves and flagged no conspicuous overload or persistent masking. They nevertheless misidentified the ending synth as a guitar and placed some changes several seconds early. These are limited screening observations, not a claim of professional quality. Four completed reviews reported **$0.089792** total. Olof’s subsequent verdict was negative; the new direction is recorded above.
