# Chrome After Rain

An original 136 BPM electronic piece: dark, swung garage drums, a metallic two-bar hook, elastic bass and a suspended breakdown. The aim is a piece worth hearing on its own; Strudel is the instrument, not the subject.

Olof's 2026-10-10 feedback on the previous workflow study: it felt like a tutorial, was less cool than hoped, and the speech sample was lame. He requested professional reference study and collaborating agents. This project retires the test speech and composes new material rather than polishing that fixture.

## Production brief

- Establish a memorable phrase within ten seconds; give it a contour, rests and an answer.
- Make bass and percussion interlock. Swing selected percussion, keeping strong anchors.
- Build contrast through transformed material, harmonic space and articulation, not only muting layers.
- Preserve one identity across breakdown, full return and half-time switch.
- Use original synthesized percussion and transition samples; no speech or borrowed song fragments.

Arrangement, synthesis and producer-critique agents researched independently. Their references are first-person production interviews and official technical documentation. We have not listened through the referenced artists' recordings and do not claim sonic matching.

## Reference techniques

- [Flava D, Ableton](https://www.ableton.com/en/blog/flava-d-evolution-of-a-producer-interview/): start with texture/harmony, build a coherent groove, separate kick and sub. Our application is a bass part that responds to percussion; no educational project samples are reused.
- [DJ_Dave, Magnetic](https://magneticmag.com/2022/04/dj-dave-castles-live-coding-and-the-algorave/): prioritize the musical result and rehearse coordinated transitions. Our arrangement changes rhythm, bandwidth and space together.
- [Holly Herndon, Ableton](https://www.ableton.com/en/blog/holly-herndon-new-love/): generate distinctive material, then chop and recompose it. Our reverse harmonic pickup and altered breakdown draw on this principle.
- [Silva Bumpa, MusicRadar](https://www.musicradar.com/music-tech/sometimes-swinging-all-the-elements-of-the-drums-doesnt-make-it-groove-better-breakout-producer-silva-bumpa-on-the-secret-to-creating-sub-bass-and-ukg-rhythms): separate the sub and apply swing selectively. Our clap/kick anchors remain straight, with more swing in ghost/rim accents.
- [Riaz Dhanani, Ableton](https://www.ableton.com/en/blog/deep-tech-mastery-inside-the-studio-with-riaz-dhanani/): shape transients, choose fragments carefully, and challenge a good bassline with alternatives. We compare compact hook sketches before expanding the arrangement.

All notes, patterns and samples here are original. See [make_palette.py](make_palette.py) and [sample provenance](references/palette.json). The generator uses the existing locked Python environment. Generated audio stays local and ignored; source and manifests are tracked.

## Review

Source critique, signal measurements and an audio-capable model are separate forms of evidence. The model receives actual audio, but its taste and precise timing remain unvalidated. Olof's listening verdict decides whether this artistic direction works.

Selected source: [v004](source/v004.strudel), saved in [project.json](project.json). The playback copy is `renders/v004/chrome-after-rain.wav`; the original master and five stems remain alongside it. Playback gain is +5.5 dB, with no limiter, compression or equalization applied afterward.

| Time | Musical event |
| --- | --- |
| 0:00 | Filtered hook and rim; space before the full rhythm |
| 0:07 | First bass/drum entrance |
| 0:21 | Answer phrase and brighter chords |
| 0:35 | Suspended, slower version of the motif |
| 0:49 | Full return |
| 1:18 | Half-time rhythm and altered bass articulation |
| 1:32 | Final return |
| 1:46 | Slow fragment and ending; tail to 1:56 |

### Decisions from actual production

1. Two initial hook/bass sketches exposed a poor balance. A solo comparison found the kick at −15.24 dBFS RMS and hook at −37.94 over the tested interval. Panning controls proved the renderer works; centered kick energy was hiding stereo detail. The revised mix reduces the kick and brings up the hook/harmony.
2. A fresh, neutral audio-model comparison preferred the plucked sketch over a thicker sawtooth alternative, describing more rhythmic space. This is a model preference, not Olof's taste verdict. The first review also made incorrect categorical claims about four-on-the-floor rhythm and absent effects; its text was not accepted as ground truth.
3. Producer source critique replaced uniformly short high notes with a lower phrase, a held F-sharp anchor and a distinct answer. The second answer rises to A and resolves differently.
4. Reviews of both halves of v003 described clear space and contrast but criticized repetition. v004 leaves whole-phrase gaps for the response and changes the lead's FM amount across sections. It keeps the same underlying tempo through the stretched breakdown and half-time passage; model descriptions of tempo changes are not literal measurements.
5. `duckorbit` failed in a scratch test when the target orbit had not been created. Isolated stems would also omit duck targets. This piece uses kick/bass timing instead; no renderer or sidechain workaround was added.

The three collaborating agents owned professional arrangement research, compatible sound design and critical source review. They did not independently hear playback. Actual audio was uploaded to the existing OpenRouter reviewer. Receipts stay in ignored `work/chrome-*`; the concise [evidence record](evidence.json) identifies the reviewed files and reported costs.

Final screening: the selected master and five stems completed with matching 48 kHz stereo duration and no full-scale samples. The playback copy measures −16.99 LUFS and −1.17 dBTP. Five completed audio reviews reported $0.130118 in total. The final model review criticized momentum through the transition, but also incorrectly said the half-time drums disappeared: their measured RMS is −24.44 dBFS versus −24.40 in the preceding return. Preserve its criticism as a hypothesis for human listening, not evidence of a missing part. Nineteen Python tests and Ruff passed; the renderer itself was unchanged.

### Reproduce

From `apps/music`, after the normal `uv sync --locked` and `npm ci` setup:

```sh
uv run --locked python projects/chrome-after-rain/make_palette.py
uv run --locked python music.py render-project projects/chrome-after-rain/project.json --revision v004 --out projects/chrome-after-rain/renders/new-v004 --timeout 180
uv run --locked python music.py mix projects/chrome-after-rain/renders/new-v004/master/render.wav --gain-db 5.5 --out projects/chrome-after-rain/renders/new-v004/chrome-after-rain.wav
```

Generate the palette only when its assets are absent; the script refuses to overwrite existing sounds. Render to a fresh directory. Source and generated samples are reproducible; fresh reverb renders may differ, so retain the selected master. Four short sketches and the earlier full drafts remain preserved, including source-only v002, which was superseded before a full render.
