# Big Softie

An original 19.5-second hand-painted anime-style cel stop-motion short about a shy puppy and an unexpectedly gentle Rottweiler.

## Watch

- Final film: [renders/big-softie.mp4](renders/big-softie.mp4)
- Poster: [renders/poster.jpg](renders/poster.jpg)
- Revised master: [renders/big-softie-v3.mp4](renders/big-softie-v3.mp4)
- Previous cut: [renders/big-softie-v2.mp4](renders/big-softie-v2.mp4)
- First draft: [renders/big-softie-v1.mp4](renders/big-softie-v1.mp4)

## Motion study

[Dense nuzzle experiment](experiments/dense-nuzzle.md) compares twelve reviewed poses with a 60 fps interpolation pass. [Watch the four-second comparison](renders/dense-nuzzle-comparison.mp4). This separate study preserves the v3 film above.

## Production

[Brief](BRIEF.md), [shot plan](STORYBOARD.md), [generation prompts](generation-prompts.md), [settling prompts](settling-prompts.md), and [review](REVIEW.md) describe the production and iteration.

Artwork was generated with the built-in image tool. The exact routed model variant was not reported. The park is a fixed painted plate; the dogs use sixteen original character drawings, eight mirrored derivatives, and seven new paired settling drawings. HyperFrames performs deterministic cel placement, pose exposure, camera framing, cuts and final audio assembly. The original piano/celesta score is written in `scripts/score.swift` and rendered locally with Apple's system instrument bank. No borrowed film soundtrack is used.

All artwork, failed attempts, derived cels and renders are preserved locally under `assets/`, `renders/` and `review/`. These media directories are ignored by Git. The repository contains editable tooling and production records; a Git checkout alone does not contain the generated artwork.

## Rebuild

From this directory on the production Mac:

```sh
npm ci
node scripts/prepare-cels.mjs puppy-run puppy-acting rott-bow rott-run
node scripts/mirror-cels.mjs
node scripts/prepare-settling.mjs settle-a settle-b settle-c settle-d settle-e settle-f settle-g
swift scripts/score.swift
ffmpeg -i assets/score.wav -af loudnorm=I=-22:TP=-2:LRA=9 -ar 48000 -c:a pcm_s16le assets/score-master.wav -y
node scripts/build-film.mjs
npx hyperframes@0.8.33 check --strict
npx hyperframes@0.8.33 render --quality high --fps 24 --workers 2 --strict-all --output renders/big-softie.mp4
```

`extract-alpha.mjs` is a one-time preparation step for the opaque source sheets and paired settling drawings. Their originals are preserved with `-opaque-original` suffixes; do not run it again on the prepared sources. The score renderer requires macOS AVFoundation and the system instrument bank. No persistent server or paid cloud compute is needed.
