# BILLIONS — moving components

[Watch the three-second silent prototype](output-v007/billions-motion.mp4) · [Compare with the previous glimmer](output-inspection-v007/before-after.mp4) · [Interactive player](index.html)

Olof likes v014's preserved visual quality but finds its glimmering motion barely noticeable. He approves a three-second BILLIONS experiment with independently moving letters and ornaments. The selected result uses an eighteen-part 2D cutout rig: eight letters, a crown, four medallions/starbursts, four ribbon regions and an interior filigree region. Original surface colors remain intact.

## Choreography

- **0–0.95 seconds:** eight letters arrive in a 67 ms stagger, alternating from above and below. Translation, rotation, compression and a short overshoot give them distinct arrivals.
- **0.3–1.95 seconds:** the crown opens, medallions rotate, and ribbon regions expand into the composition. The interior detail appears after the letters settle.
- **1.95–2.52 seconds:** the assembled design holds. This actual timeline frame, not only a diagnostic reconstruction, matches the original RGB pixels at native size.
- **2.52–3.0 seconds:** ornament clears, then the letters scatter in alternating directions. Clearing the background first avoids exposing letter-shaped holes left in a flattened image.

The camera stays fixed. Moving elements carry the sequence; there is no exposure or shimmer animation. The source's red and blue palette stays unchanged.

## Separation and rendering

`extract-rig.py` isolates the eight largest connected ivory faces using a BILLIONS-specific color threshold, fills small interior gaps, and includes a six-pixel contour margin. It converts only those control masks into paths. It never retraces the artwork's color or engraving. The named glyphs and ornament regions remain in `rig.json`.

The reusable [plate splitter](../../../../tools/artwork/split-plate.js) assigns source pixels to ordered authored masks and returns cropped component canvases. All source pixels have one owner. The ornament renders first; opaque letters render over it with normal compositing so engraving stays solid when parts overlap. Adding their brightness together produced transparent-looking letters in early attempts and was rejected.

This is a **cutout rig**, not a font, a recovered 3D model or complete hidden surfaces. The choreography avoids revealing unpainted space behind seated letters. Individual pieces retain some neighboring shadow/edge detail; arbitrary recomposition would require more authored component artwork. The mechanism now supports genuinely independent glyph transforms, while v014 controlled only surface exposure.

## Screening

The assistant inspected the isolated glyph atlas, encoded overview, all twelve consecutive arrival and exit frames, intermediate full-size frames and the assembled proof. The selected entrance reads clearly at contact-sheet size. The full design remains crisp at its hold. Olof subsequently says, “Yeah that's definitely more movement. Good job!” He approves combining this motion with NEXT and KEEP UP in a six-second silent rhythm study. This confirms the movement improvement, not parity with the film references.

Validation: 72 frames, 24 fps, three seconds, 1600×900, no audio, deterministic seeks, no browser errors or external network requests, full FFmpeg decode and browser playback through the end. Both the diagnostic assembly and actual timeline hold reproduce the 1672×941 original exactly. The browser player also checks completion, seeking, assembled view and a 390-pixel layout. Consolidated results are in [results.json](results.json).

Renders use a 3200×1800 canvas and downsample before H.264 encoding. MP4 remains lossy; source/native proofs are the quality reference. Pixel-change measurements confirm substantially more activity than the old lighting study but are not artistic scores.

## Iterations and independent review

All earlier outputs remain local:

- v001: authored approximate contours; visible leftover edges and additive overlaps.
- v002: wider masks captured too much surrounding ornament.
- v003: connected ivory-face extraction greatly improved isolated glyphs.
- v004: opaque foreground letters fixed the see-through overlaps.
- v005: removed a second letter wave, delayed interior detail and cleared ornament earlier on exit. Moving letters again after assembly had exposed holes and detached shadows.
- v006: removed red/blue channel-swap flashes, which muddied the palette.
- v007: same selected animation, with the player layout corrected for narrow viewports.

A completed Claude Opus 5.5 consultation reviewed the v003 still evidence independently. It found the arrival and exit clearly legible, identified additive blending as the primary defect, warned about holes during exit, and recommended removing muddy color flashes. Its findings agreed with the compositing and choreography corrections underway and informed the final palette decision. Claude did not claim to watch normal-speed playback. Raw consultation JSON is local.

## Reproduce

From the repository root, with the app's Animate browser dependencies and ffmpeg installed:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/billions-motion-v015/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/billions-motion-v015/render.mjs apps/canvas-animation/projects/title-sequence-study/studies/billions-motion-v015/output-new
node apps/canvas-animation/projects/title-sequence-study/studies/billions-motion-v015/screen.mjs apps/canvas-animation/projects/title-sequence-study/studies/billions-motion-v015/output-new
```

The source is the versioned `../fidelity-v014/assets/billions.png`. The HTML is self-contained; no server is needed. Output must be a new directory. Render output preserves every frame, the movie, native proofs, glyph atlas, consecutive-frame sheets, poses, validation and frozen implementation.

`verify-quality.py RENDER-DIRECTORY NEW-INSPECTION-DIRECTORY` checks native fidelity and constructs the side-by-side movie. That comparison additionally needs the preserved `../fidelity-v014/output-motion-v004` baseline frames. `extract-rig.py SOURCE RIG NEW-OUTPUT` regenerates letter controls while preserving the named ornament definitions. Python dependencies use PEP 723 and `uv run --script`; no system Python packages are installed.
