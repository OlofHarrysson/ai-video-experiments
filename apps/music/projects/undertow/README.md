# Undertow — club groove test

A 134 BPM, 16-bar bass-and-drums study with an effect tail, made after Olof rejected Soft Focus as too game-like and childish. His direction is techno/club music with a heavy bassline, strong drums, less melody and an adult, underground edge; it need not be angry.

Listen to `renders/v002/undertow.wav`. This is a short direction test, not a finished arrangement. The groove starts immediately. Human listening feedback comes before expanding it into another full track.

## Production choices

- A four-on-the-floor 909 kick and a syncopated rolling F bass pedal carry the piece. A rare E-flat is the only bass pitch departure; there is no lead tune or moving chord progression.
- The bass combines a low sine/FM body, a filtered saw layer and a restrained low growl. Their onsets occupy spaces around the kick.
- Closed/open hats, a quiet swung shaker and lowered percussion supply momentum. Sparse filtered minor stabs and a dissonant background layer add texture.
- The reference library remains available, but Olof's explicit direction now takes precedence over the earlier emphasis on sustained melodic foregrounds. No reference recording or stock speech appears in this composition.

Samples are the retained [909 drums](../practical-dogfood/drum-sources.json) and original percussion from the [Chrome palette](../chrome-after-rain/references/palette.json). The render receipt hashes all local assets. No new service, plugin, renderer behavior or automatic paid retry was introduced.

## Reproduce

From `apps/music`, with retained samples present:

```sh
uv run --locked python music.py render-project projects/undertow/project.json \
  --revision v002 --out outputs/undertow-v002 --timeout 150
```

[Source](source/core-v002.strudel), [recipe](project.json), [evidence](evidence.json).

## Screening

The v001 core audio model review described the piece as carried by interlocking drums and substantial low bass, with no prominent high-register tune. It reported no obvious overload or masking. These are narrow screening observations, not evidence that the result meets Olof's taste. One completed OpenRouter review reported $0.017644. Master and isolated stems provide the independent level and clipping checks.

The repeated direction miss is recorded as friction incident AF-20261010-133514, related to AF-20261010-130533. The practical change is a short audible groove checkpoint before full arrangement.

After inspecting the isolated stems, v002 raises the rolling bass layers roughly 2.5 dB and lowers the kick 1.4 dB. The notes, rhythm and sparse texture are unchanged. The paid review covers v001; it is not represented as a separate review of v002. The earlier renders and listening copy are preserved.

The 32.24-second v002 playback copy measures -13.71 LUFS and -1.29 dBTP, without clipping, using +0.00 dB constant gain from the master. Master and three stems are aligned at 48 kHz stereo. Bass stem RMS rose +2.440 dB and drum stem RMS changed -1.365 dB. Nineteen Python tests and Ruff passed. Olof’s verdict is pending.
