# Remotion

Programmatic video with [Remotion](https://www.remotion.dev/): React components rendered frame by frame, previewed and edited in Remotion Studio, and rendered in parallel with the bundled ffmpeg. Soundtracks are synthesized with Tone.js on the same beat grid. It sits alongside the hand-rolled [canvas animation](../canvas-animation/README.md) pipeline.

- [AI Filmhack: frenzy cut](projects/filmhack-frenzy/README.md): a 25.6-second high-energy Reel with a synthesized 150 BPM score.
- [Watermelon shape guides](projects/watermelon-guides/README.md): SVG placement guides and a seven-frame comparison of independent, reference-conditioned and masked image generation.
- [The Moon Fisher](projects/moon-fisher/README.md): a calm pixel-art short with no dialogue, drawn in code. In planning.

Remotion's own AAC track keeps the encoder's priming as audio: 43 ms of delay, enough to put hits visibly late. Mux the mastered soundtrack with ffmpeg instead, as the frenzy cut's `scripts/render.mjs` does, and check sync on the decoded file.

Remotion is free for individuals, companies of up to three people and nonprofits; larger companies need a company license ([terms](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)). Each project keeps its own dependencies, fonts and renders locally, all ignored by Git.
