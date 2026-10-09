# Character screen test

A local experiment for Olof: **rough 3D performance → AI-styled video**, within a $50 project budget. Olof directs the character conversationally; the agent handles the production tools. The script and stock voice are placeholders.

**Paused on 9 October 2026 at Olof's request.** The final test preserves broad arm and head motion through Kling styling, with small timing drift and unresolved lip-sync. No further generation is planned. This app was moved into AI Video Experiments from the standalone `avatar-studio` checkout; all local media was retained and hash-verified. The original Git history is retained locally in `.private/migration/original.git` at commit `673dc65`.

## Watch

The local service is stopped while this experiment is paused. When resuming, start this app through Terminal Manager and use its returned URL. The home page contains a source / animated-film / clay comparison; `/motion.html` contains the silent motion test. The historical review address was **http://localhost:3044/**. Full-size local outputs and notes are under the disclosure below each video.

Terminal Manager owns the local service: project `/Users/olof/git/ai-video-experiments/apps/avatar-studio`, service `web`, command `npm run dev`. Register the new path when resuming; the previous path's service has been stopped. The loopback server uses the port assigned through `PORT`. Generated videos stay in ignored `.private/restyle/` and `.private/motion/`; the local server serves them for review. They are not included in the static build or GitHub repository.

## What this tests

The source reuses the earlier Three.js prototype: a fictional character with glasses, brown hair and a terracotta top. Its modest head movement, blinking and audio-energy mouth animation are deliberately crude. Two Kling O3 Pro video edits receive the exact same full 12.2-second performance and different visual instructions.

The intended result is a better-looking **rendered video**, not a newly rigged 3D asset. Retaining speech audio does not establish correct lip-sync. A still image or newly invented animation would not establish performance preservation either.

[Experiment results, limitations and reproduction](docs/experiments/restyle.md) · [Exact inputs, request IDs and budget](docs/experiments/restyle.json)

The completed [eight-second motion test](docs/experiments/motion.md) is at **http://localhost:3044/motion.html**. Kling preserves both waves and head turns with small transition delays, improves the look, and retains some crude body and arm structure. It is silent and does not test lip-sync.

For future animation work, use an existing rig and authored motion. Improving the custom rig or expanding the appearance controls is outside the current experiment.

## Budget and access

Ceiling: **$50**, with no recurring subscription. The original two video jobs are approximately $3.42692; the Qwen3-TTS stock voice is $0.01557; the eight-second motion edit is $1.12. **Estimated cumulative spending: $4.56.** Duration rounding and the invoice are not reconciled.

No new API key was needed. The already-connected Fal account handles paid generation through Codex; this web app makes no paid calls. A future direct server integration would require `FAL_KEY`, but is not implemented. No photo or voice sample from Olof was uploaded. Qwen's stock Aiden voice is not a clone of Olof. Speech provenance is in [generation.json](docs/generation.json).

## Source workspace

The earlier authoring prototype remains at `/studio.html` for agent-operated source production. It supports:

- Orbitable Three.js geometry, appearance presets and material adjustments.
- Simple blinking, head/arm motion and speech-volume-driven mouth movement.
- Stock AI sample, installed macOS text-to-speech, audio import, playback and local WebM export.

Export records the visible canvas in real time; keep the tab visible. Files save under `.private/exports/`. Local speech requires macOS. The sample and imports do not. There is no phoneme alignment, voice cloning, GLB/VRM export, background renderer or external character import.

## Research

- [Hosted competitors](docs/competitors.md): HeyGen, Hedra, Synthesia, Captions/Mirage, D-ID, Tavus and Sync Labs.
- [Open models and real 3D](docs/open-models.md): Qwen, Wan, LongCat, EchoMimic, InfiniteTalk, MuseTalk, MetaHuman and VRM.
- [Original source-workspace verification](docs/verification.md).

## Development

```sh
npm ci
npm run verify
node scripts/build-comparison.mjs
node scripts/build-motion-comparison.mjs
```

The style comparison command requires local `source.mp4`, `film.mp4` and `clay.mp4` under `.private/restyle/`; the motion comparison requires `source.mp4` and `styled.mp4` under `.private/motion/`. Both require FFmpeg, perform only local postproduction and never submit paid jobs. Use Terminal Manager for service lifecycle. The Vite build verifies the frontend bundles; the local speech/export APIs and ignored videos require the development server.

## Code map

- `index.html`: quiet video review page.
- `motion.html`: silent source / styled motion comparison.
- `studio.html`, `src/main.js`, `src/style.css`: source production workspace.
- `src/avatar.js`: procedural placeholder character and performance API.
- `src/speech-server.js`: local macOS speech and export storage.
- `scripts/build-comparison.mjs`: local comparison, contact sheets and media metadata.
- `scripts/build-motion-comparison.mjs`: uncropped motion comparison and timestamp checkpoints.
- `test/speech.test.js`: speech input boundary checks.

Code, research and small evidence files are tracked in the parent [AI Video Experiments repository](https://github.com/OlofHarrysson/ai-video-experiments). Keep generated media and secrets in ignored local paths. No cloud deployment is configured.
