# Canvas animation

Motion graphics written in TypeScript and drawn on an HTML canvas. Every frame is a pure function of time, so the browser preview and the headless render match exactly; soundtracks are synthesized in the same page with the Web Audio API and share the film's beat grid. This workflow is separate from diffusion (Deforum, ComfyUI), Blender and stop-motion.

- [AI Filmhack promo](projects/filmhack-promo/README.md): a 30-second Instagram Reel for the AI Filmhack event, with an original synthesized score.

Rendering uses the local Google Chrome through Playwright, and ffmpeg for encoding; no cloud compute. Downloaded fonts, dependencies and renders stay inside each project and are ignored by Git.

## Animate skill

[Animate](../../.agents/skills/animate/SKILL.md) provides procedural drawing styles, story and storyboard reviews, synthesized scores, rendering and reference analysis. Codex discovers the repo-local `.agents/skills/animate` copy; `.claude/skills/animate` links Claude Code to the same copy. Invoke `$animate` in Codex or `/animate` in Claude Code. New pieces belong in `projects/<name>/`, with shared custom styles in `styles/<name>/`.

The skill uses Node 20+, its own pinned Playwright dependency and matching Chromium, plus ffmpeg/ffprobe on PATH. The existing Filmhack project's Chrome renderer is separate. From the repository root:

```sh
npm ci --prefix .agents/skills/animate
# Only if the matching Chromium is not already cached:
node .agents/skills/animate/node_modules/playwright/cli.js install chromium
```

Analyze a short reference video with:

```sh
uv run --locked --script .agents/skills/animate/tools/measure/shotlog.py path/to/reference.mp4
```

`uv` manages NumPy from the script's dependency metadata and lockfile; no system Python installation is modified. The upstream analyzer estimates cuts, holds, stepped motion, audio onsets, loudness and spectral brightness. Use clips of at least two seconds with an audio stream. It loads decoded frames into memory, rounds fractional frame rates, and uses heuristics; validate its findings against playback. Its flicker metric compares four-frame lags despite the upstream two-frame comment, so do not treat it as a validated flicker detector.

Faster-whisper and its model downloads are disabled. Narration takes still work, with measured line durations and explicitly estimated word timestamps. No voice-generation connector is required. Burned-in subtitle previews require an ffmpeg build with the `subtitles` filter; use export's `--no-captions` on the current minimal ffmpeg build. This does not remove narration audio or the animation's own drawn captions.

The vendored skill retains its MIT license and records its upstream revision in [upstream.json](../../.agents/skills/animate/upstream.json). Local adaptations use portable question tools, local dependencies, estimated narration timing and browser-drawn review labels. Preserve these changes when updating upstream.

Installation validation (2026-10-07): the six-second beat-cut template built and exported at 1080×1920/24 fps; deterministic frame sampling, cut-grid, story-arc, text and dead-beat checks passed. The NumPy analyzer processed that MP4 successfully. Synthetic audio verified measured line durations and estimated word flags; generated voice quality was not tested. Smoke-test files are kept under ignored `work/animate-install-smoke/`. Skill paths resolve to the same file for both assistants; in-session discovery is checked on the next turn.
