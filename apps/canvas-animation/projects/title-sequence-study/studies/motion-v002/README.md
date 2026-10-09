# Motion study v002

Eight original motion behaviors, built after Olof found v001 too restrained. [Tooling plan and deferred ideas](../../MOTION-PLAN.md). The sample words do not select a film theme. No reference pixels are used.

## Review

- [Catalogue](output/catalogue.mp4): 32 seconds, eight labeled four-second demonstrations.
- [Escalating edit](output/escalation.mp4): 17 seconds, 21 shots; holds shorten from four seconds to two, one, half and quarter seconds, with rising movement amplitude. Reuses the eight behaviors, not 21 unique designs.
- [Motion phases](output/motion-phases.png): four times per behavior, for inspecting construction and deformation.
- [Overview](output/motion-overview.png) and [edit overview](output/edit-overview.png).

Both videos are silent, 1280×544 at 24 fps. Sound escalation remains deferred. The interactive [preview](index.html) has scene selection, scrubbing and play/pause; run font preparation before opening it locally.

| # | Behavior | What moves |
| --- | --- | --- |
| 1 | Neon ignition | Custom strokes draw on, letters separate and turn, dashed enclosure moves. |
| 2 | Particle pressure | Hollow circles form MORE, then scatter along deterministic trajectories. |
| 3 | Elastic blackletter | Sampled font contours bend, with offset colored outlines. |
| 4 | Letter impact | Individual glyphs tumble into place, stretch and leave at staggered times. |
| 5 | Contour vortex | Seventeen outline copies rotate, warp and expand into a knot. |
| 6 | Cut and shear | Horizontal slices of blackletter move independently. |
| 7 | RGB rupture | Colored dot screens assemble, rotate and separate. |
| 8 | Poster collision | Increasingly frequent word impacts build a layered composition. |

## Tooling

GSAP 3.15.0 and OpenType.js 2.0.0 are exact project-local dependencies in `package-lock.json`. GSAP timelines are paused and sought to an explicit time for every frame; the live ticker is disabled. Playback and export use the same render functions. A small deterministic index-based pseudo-random function sets particle trajectories; there is no frame-history accumulation.

`tools/prepare-fonts.mjs` reads two bundled OFL font files, extracts whole-word and individual-letter outlines, and samples curves into points. Generated `tools/font-data.js` is ignored and recreated before rendering. This supports deformation, not automatic correspondence between different words. `tools/motion-kit.js` provides timeline envelopes, shape drawing, mask sampling and deterministic positions. Scene-specific art stays in this study's `scenes.js`.

The renderer reuses Animate's existing Playwright/Chromium install and FFmpeg. No global npm packages, system fonts, GPU service or cloud spend. Local scripts/font data make this a project study rather than Animate's single-file build format. The vendored skill is unchanged.

## Reproduce

From this project directory:

```sh
npm ci
npm run render:motion
```

Outputs are ignored. Rendering refuses to overwrite an existing output directory. Preserve it under `output-<revision>/`, or set `MOTION_OUTPUT=output-<new-name>` before rendering. Use `npm run render:motion -- --stills` for a quick inspection pass. To prepare only the browser preview: `npm run prepare:fonts`.

## Validation and assessment

All eight behaviors render identical PNG hashes at the same time after seeking forward and back. The changed-pixel fractions between 0.4 and 1.8 seconds are 11.6–46.4%; this catches nearly static scenes but does not measure artistic quality. Scene selection, scrubbing, playback advancement and paused-frame stability passed through Playwright. See `output/report.json` for the cut schedule and checks.

Assistant inspected the overview, four phases per scene, the montage overview and an eight-frame cut window. These establish construction and selected temporal behavior, not an independent real-time playback judgment. The neon now has actual stroke/letter motion; blackletter deformation and outline tangles have visibly different states; the dots intentionally lose legibility during dispersal. Large contours, particles and impact typography intentionally leave the frame during chaotic phases. This is a motion vocabulary prototype; its repeated palettes and two base fonts still provide less graphic variety than the film reference. Human taste review remains pending.

Next: Olof reviews the movement and combinations. Refine selected behaviors, expand type/graphic variety, then design sound and choose a theme. GPU effects remain a targeted future option rather than an installed unused dependency.
