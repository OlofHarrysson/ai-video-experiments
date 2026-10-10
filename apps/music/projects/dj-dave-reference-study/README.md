# DJ_Dave audio reference study

Olof supplied DJ_Dave's [official YouTube channel](https://www.youtube.com/channel/UClP415zhIvcwjjuFj1o3V3g) on 2026-10-10 after finding Chrome After Rain too much like a computer game. The task is to acquire actual audio references and exercise the comparison workflow. Olof will supply more specific taste direction later; this study does not select a final genre or produce another song.

## Reference library

The [channel snapshot](channel-snapshot.json) enumerates all 79 accessible uploads using YouTube's Data API, then sorts their current view counts. These are the five most-viewed **song-length uploads, between two and six minutes**. This is a channel-specific ranking, not a claim about streaming popularity across platforms. Extended performances and short process clips are excluded from the working set.

| Reference | Views at retrieval | Full local audio | Matched study excerpt |
| --- | ---: | --- | --- |
| [Cycles — DJ_Dave + Switch Angel (Live)](https://www.youtube.com/watch?v=Mbeku_nj0Nk) | 209,642 | [WAV](references/assets/decoded/cycles.wav) | [28 seconds](references/assets/matched/01-cycles.wav) |
| [Castles (Live Coded Visualizer)](https://www.youtube.com/watch?v=IqhKVEsSkls) | 113,583 | [WAV](references/assets/decoded/castles.wav) | [28 seconds](references/assets/matched/02-castles.wav) |
| [Airglow (Visualizer)](https://www.youtube.com/watch?v=ure6OT0LwtM) | 79,960 | [WAV](references/assets/decoded/airglow.wav) | [28 seconds](references/assets/matched/03-airglow.wav) |
| [Array (Official Music Video)](https://www.youtube.com/watch?v=w2s1DK1w3WI) | 79,801 | [WAV](references/assets/decoded/array.wav) | [28 seconds](references/assets/matched/04-array.wav) |
| [Easy (Live Coded Video)](https://www.youtube.com/watch?v=JiQHclg_648) | 60,310 | [WAV](references/assets/decoded/easy.wav) | [28 seconds](references/assets/matched/05-easy.wav) |

The [57-minute hybrid set](https://www.youtube.com/watch?v=E1K6Sv-oIb0) leads the overall channel at 215,282 views. The [13-minute Easy performance](https://www.youtube.com/watch?v=YvsoWehBbec) has 118,014 views. Both remain in the inventory; neither was downloaded in this focused song-reference set. A hybrid set may include music from other artists.

All five full audio streams are retained as downloaded Opus/WebM alongside their metadata, plus float WAV decodes. WAV conversion does not restore quality absent from the YouTube stream. Float decoding preserves possible lossy-codec overshoots instead of clipping them into PCM16. Audio and raw download metadata are local and Git-ignored. These recordings are reference material, not sample assets for reuse in an original composition.

## Comparison setup

See [manifest.json](manifest.json) for source URLs, hashes, formats, selection and excerpt bounds; [measurements.json](measurements.json) records the matched clips.

- Reference excerpts use a consistent 30–58-second window. They are not claimed to be the chorus or best part of each song.
- Our comparison is Chrome After Rain v004's full return, starting at 49.411765 seconds, also 28 seconds long.
- Existing `music.py match` attenuates copies to the quietest measured excerpt: **−18.07 LUFS**. No compression, EQ or resampling was applied. All six copies measure within 0.01 LUFS of the target, with no full-scale samples.
- [Pair 01](references/assets/pairs/pair-01.wav): our sketch, then Cycles. [Pair 02](references/assets/pairs/pair-02.wav): Castles, then our sketch. Each has 28 seconds of A, two seconds of silence and 28 seconds of B.
- Pair 03 repeats the exact same Castles excerpt twice. Sample equality and the digital-silence separator were verified. The audio model was not told which comparison was the control; it correctly reported identical excerpts. This is one narrow successful control, not validation of its taste or subtle production diagnosis.

The model receives actual waveform input with [this neutral comparison prompt](comparison-prompt.txt), without artist identities, source code or condition labels. Other references use [the descriptive prompt](reference-prompt.txt). Private provider receipts are under `apps/music/work/dj-dave-reference/`. Parent-agent text is not a claim of independently hearing playback.

Read the [first audio comparison findings](findings.md) and [validation evidence](evidence.json). Six completed reviews reported $0.141966. The recurring model-described contrast is sustained foreground performance and supporting texture versus our mostly short, isolated plucks. Exact processing claims remain unverified; no new song was made in this study.

## Working commands

From `apps/music`, the acquisition route was public `yt-dlp` bestaudio, with no cookies or login required:

```sh
uvx yt-dlp --js-runtimes node --no-playlist --no-progress --retries 0 --fragment-retries 0 --no-overwrites -f bestaudio --write-info-json --paths projects/dj-dave-reference-study/references/assets/originals -o '%(id)s.%(ext)s' 'https://www.youtube.com/watch?v=Mbeku_nj0Nk'
```

Repeat with the other source URLs when restoring the library. Existing originals are preserved; use a fresh destination for a new acquisition snapshot. The recorded download tool version was `2026.08.19`; all five selected format 251, Opus, 48 kHz stereo.

For a fresh decoded file and an excerpt:

```sh
ffmpeg -nostdin -v error -n -i INPUT.webm -vn -c:a pcm_f32le OUTPUT.wav
uv run --locked python music.py excerpt OUTPUT.wav --start 30 --duration 28 --out NEW-EXCERPT.wav
uv run --locked python music.py match REFERENCE-EXCERPT.wav CANDIDATE-EXCERPT.wav --out NEW-COMPARISON
```

Keep the original files untouched and retain each new set under a fresh path. Pair assembly uses the matched waveforms plus two seconds of digital silence; the review adapter saves the submitted audio hash and prompt.

## Workflow lesson

The previous composition was expanded from written production advice and uncertain model critique before an audible target had been established. Technical success did not resolve sound selection or taste. This study supplies the missing reference corpus. The next creative experiment should be a short sound/groove sketch that tests specific reference-derived traits, while preserving the distinction between model hypotheses and Olof's preferences.

This process failure is recorded as **AF-20261010-130533** in the central agent-friction log. It does not authorize changes to global personalization or imply that these five tracks are Olof's individually approved favorites.
