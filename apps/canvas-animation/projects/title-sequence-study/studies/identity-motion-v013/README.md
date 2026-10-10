# BILLIONS / NEXT / KEEP UP — motion studies

Olof approves the three richer v012 directions: “Yeah these are pretty cool. Sure let's do those.” This authorizes developing the selected artwork. The rejected v011 storyboard is not reinstated. This bounded sprint makes three short silent motion studies using the approved style frames, before committing to a full AI intro narrative.

## Intended outcome

Preserve the approved graphic richness, then make movement specific to each design. Each study lasts four seconds at 24 fps, 1600×900; a twelve-second review reel presents all three. Maintain medium-high local activity with readable holds, without a slow opening, sustained strobing or whole-image camera drift. No soundtrack or numeric factual claims.

- BILLIONS: engraved ink, a brief registration event, a travelling emphasis through the security ornament. Keep the word and its fine linework intact.
- NEXT: outline / solid / repeated announcement states, directional reveals and contrasting layer events. Preserve the angled rails and scale relationships.
- KEEP UP: directional reflections travelling through red enamel and gold edging, with a composed hold that shows the finished lettering.

## Validation

Compare resolved frames with the v012 sources before animation. Reject transfers that materially degrade fine detail or surface quality. Render deterministic frame samples, screen complete shot overviews and consecutive event frames, inspect encoded output, check silent playback and keep original media/earlier attempts. Human approval of the targets is not automatic approval of reconstruction or motion.

The existing repo-local Animate workflow and existing tracing/Canvas tooling remain the basis. Source generations live independently in v012/reference and in the recorded original generation directory. No new image generation, source raster playback, font system or full intro storyboard is assumed.

## Result

[Watch the twelve-second reel](output-motion-v002/three-identities.mp4) · [Interactive review](index.html)

Three four-second studies, 1600×900 at 24 fps, silent. Individual exports live beside the reel as `billions.mp4`, `next.mp4` and `keep-up.mp4`. The local interactive review has play/pause, scene selection and frame seeking. Rebuild it from the committed compressed geometry with `node build.mjs` from this directory.

- **BILLIONS:** staggered face-ink assembly, stable ornament, travelling illumination through the engraved pattern, one red/blue registration accent. Its first entrance moved whole vertical strips and broke the ornament; v002 keeps the darker ornament in place and moves only the visible face ink. The registration accent begins around 1.58 seconds.
- **NEXT:** angled face/foreground reveals, a single outline interruption at 1.5 seconds, an offset foreground-ink return and opposing light passes. The first outline was nearly invisible; v002 derives a complete three-pixel interior boundary. The large word remains readable through the outline event.
- **KEEP UP:** red enamel, gold edging and bright reflections have separate masks and light trajectories, with two restrained star glints. This is the quietest movement study. The surface is a painted approximation with moving light overlays, not a physically relit 3D object.

The assistant recommends NEXT as the most useful motion direction of these three. BILLIONS has a stronger graphic identity than the rejected v011 board but still needs cleaner small engraving. KEEP UP preserves the swashes and material contrast but its dense trace remains rougher than the generated target. The human verdict is pending. These studies do not establish reference-film quality or settle the full edit's rhythm.

## Transfer and control

The six-ink BILLIONS and 48-color KEEP UP traces were rejected after side-by-side inspection: the former strips fine engraved marks, the latter posterizes reflections severely. Denser 256-color traces retain more of the approved composition. Polygon tracing with 0.1-pixel cleanup was selected over the dense spline versions: similar detail with smaller geometry and faster proof rendering. All attempts remain in separate ignored output directories.

| Design | Selected paths | Compressed geometry | Remaining limitation |
| --- | ---: | ---: | --- |
| BILLIONS | 33,826 | 852,477 bytes | Fine face hatching is still degraded; many tiny paint fragments |
| NEXT | 241 | 8,261 bytes | Flat inks; no hidden geometry behind overlaps |
| KEEP UP | 27,917 | 717,347 bytes | Rougher bevels and less smooth reflections than source |

`assets/provenance.json` records extraction parameters, source hashes and geometry hashes. These are ordered paint paths, **not complete glyphs or a reusable font**. The source PNGs are used only for extraction/comparison. The runtime draws the paths, caches that code-rendered composition in canvases, and derives visible color/material masks from its pixels. No source PNG, image URL or embedded bitmap is used in playback. Gzipped JSON is a storage format for path commands, not an image. `build.mjs` decompresses it into a self-contained local HTML file.

This approach gives control over visible ink, local assembly, timing, registration and light. It does not recover occluded letter parts, surface normals or semantic ornament groups. Dense tracing preserves more appearance at the cost of editability. A smooth new lighting model or independent overlapping glyph movement would require deliberate material/shape reconstruction.

## Validation and screening

Selected export: `output-motion-v002`. Its 288 frames contain 225 distinct images: 78 / 51 / 96 per study. Repeated frames include deliberate holds; uniqueness is not a quality score. Seek determinism, no runtime errors, no external network requests, silent media streams and full FFmpeg decoding pass. Browser playback reaches the twelve-second end; play/pause, scene selection, seeking and 390-pixel viewport overflow checks pass. Reports are `report.json` and `screen-report.json` beside the movie.

Assistant visual inspection covered source/vector comparisons, a 24-frame motion overview, twelve consecutive frames each of BILLIONS assembly, NEXT outline return and KEEP UP glint, and 24 frames sampled from the encoded MP4. This checks local defects and persistence; it is not a human normal-speed rhythm judgment. Thin chromatic lines soften in the encoded export. The v001 render and frozen source snapshots are preserved.

## Reproduce

From this directory, with the existing repository Playwright and FFmpeg setup:

```sh
node build.mjs
node render.mjs output-motion-new
node screen.mjs output-motion-new
```

The renderer refuses to overwrite an output directory. It writes frame PNGs, three individual videos, the combined reel, contact sheets, a frozen runtime and a technical report. The generated `index.html` and output directories are ignored; compressed vector assets, source, configuration and provenance are committed. No new packages, paid generation, dev service or soundtrack were needed.
