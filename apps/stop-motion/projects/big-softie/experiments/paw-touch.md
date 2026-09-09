# Paw-touch motion study

## Result

[Watch the four-second clip](../renders/paw-touch-v1.mp4): 1920×1080, 60 fps, 240 frames, silent. The puppy lifts a paw, reaches forward and places it on the resting Rottweiler's paw. The adult closes his eyes contentedly after contact. A held opening and ending frame the two-second action.

This pass makes a more readable gesture while removing whole-character repaint drift. It uses eleven selected puppy poses and a separate adult eyelid edit, assembled into twelve anchors. RIFE adds ninety-nine intermediate frames; nine final holds complete the 120-frame motion source. The delivered clip adds thirty opening and ninety ending hold frames. There are 111 unique finished motion frames. The previous film and nuzzle comparison are preserved.

The final scene concentrates on the paw lift and touch. It does not include a walking cycle or body translation: support paws, character silhouettes outside the acting leg, and the park remain stationary. This is deliberately limited cel animation, not full-body animation or a replacement for the complete film.

## Artwork and controls

Three built-in image-generation calls produced two six-pose puppy sheets and one adult blink edit. [Exact prompts and references](paw-touch-generations.json) are preserved. The tool did not explicitly report its routed model variant. Every original image remains under `assets/paw-touch/source/`.

The first sheet established the action. It was inspected before requesting the second sheet's missing intermediate poses. All twelve puppy candidates were extracted and reviewed; pose 1 was omitted because its early ground reach weakened the intended lift-and-touch action. The selected order is `0, 6, 7, 2, 8, 3, 9, 4, 10, 11, 5`, followed by pose 5 with the adult's eyelids closed.

The generated puppy is registered against one master drawing using unchanged head and body regions. Only the acting foreleg patch is accepted from each new pose. The rest of the puppy is copied from the master, including its head, supporting legs, tail and body texture. Small channel offsets, measured on an unchanged shoulder region, match the patch to the master's colors; the largest applied offset is four levels on the 0–255 scale. Detached toe fragments caused by registration and clipping were found during review and removed before interpolation.

The original resting adult is isolated from `assets/source/settle-e.png` along its visible silhouette. Only two feathered eyelid patches are accepted from the new blink image. The adult's body and colors are not taken from that redraw. The park is the existing plate. Staging puts the lowered puppy paw over the top of the adult's resting paw, with supporting feet fixed.

After interpolation, original pixels are restored everywhere outside the foreleg and eyelid regions. Every source-anchor change was checked to fit those regions. Every one of the 120 finished motion PNGs has exactly the same 896,050 pixels outside those regions—97.23 percent of the 1280×720 frame. This is a pre-encoding pixel guarantee; H.264 encoding is lossy.

## Review and limits

The first RIFE pair was inspected before the full run. The full sequence was reviewed with an overview, every-frame landing and blink windows, and enlarged detail sheets. The paw has intermediate positions through its descent and lands on the adult's paw. The eyelid edit has intermediate closing positions. The broad color and silhouette shifts from the nuzzle study are prevented by the fixed artwork.

The moving leg still uses inferred shape transitions and changing painted detail. At an enlarged crop, a few intermediate toe outlines soften. This experiment does not establish a solution for walking, turning, weight transfer or broad full-body acting. Human playback preference remains unconfirmed.

Final verification:

- HyperFrames 0.8.33 strict checks passed with no findings. No geometry-motion assertions were configured for this pre-rendered video; motion was reviewed from decoded frames.
- Strict final render completed; FFmpeg decoded the entire result without errors.
- FFprobe confirmed H.264, 1920×1080, 60 fps, 240 frames and 4.000 seconds.
- Actual first, action and final encoded frames were inspected; the opening and ending contain the intended scene.
- All generation originals and exact prompts exist locally. No paid cloud compute, persistent server or publishing was used.

Review artifacts are in `review/paw-touch/`: `locked-keyposes.png`, `staged-anchors.png`, first-pair and motion contact sheets, `landing-detail.png`, `blink-detail.png`, `final-opening-action-ending.jpg`, `check.json`, `probe-final.json`, and render logs. Media and review directories are ignored by Git; a repository clone alone does not contain these assets.

## Tooling and reproduction

From the project directory, using the preserved artwork and completed interpolation:

```sh
node scripts/prepare-paw-touch.mjs
node scripts/stage-paw-touch.mjs
node scripts/finish-paw-touch.mjs
node scripts/build-paw-touch.mjs
npx hyperframes@0.8.33 check assets/paw-touch/composition --strict --snapshots --at 0,0.7,1.3,1.9,2.3,3.9 --json
npx hyperframes@0.8.33 render assets/paw-touch/composition --quality high --fps 60 --workers 2 --strict-all --output renders/paw-touch-v1.mp4
```

`prepare-paw-touch.mjs` owns extraction, registration, patch color matching and fixed body pixels. `stage-paw-touch.mjs` owns the adult eyelid patch, character placement and selected anchor order. `finish-paw-touch.mjs` owns the two animation regions, pixel restoration and hold timing. `build-paw-touch.mjs` owns the standalone HyperFrames composition. No new dependencies were installed.

For a fresh interpolation run, use the existing `apps/deforum/interpolate.py` runner and local RIFE 4.25 environment. Its pinned Practical-RIFE commit is `bbfd2ea90910789a860ea3e2b32a240cd577b75e`. Commands below were executed from `apps/deforum/`; output directories must be new. Preserve existing directories and use a new versioned destination when rerunning, then point the finishing script at that reviewed version.

```sh
work/rife-session/.venv/bin/python interpolate.py ../stop-motion/projects/big-softie/assets/paw-touch/rife-input ../stop-motion/projects/big-softie/assets/paw-touch/rife-pair --source-frames 12 --source-fps 6 --multiplier 10 --pair-only
# Review the first pair before proceeding.
work/rife-session/.venv/bin/python interpolate.py ../stop-motion/projects/big-softie/assets/paw-touch/rife-input ../stop-motion/projects/big-softie/assets/paw-touch/rife-full --source-frames 12 --source-fps 6 --multiplier 10 --validated-pair ../stop-motion/projects/big-softie/assets/paw-touch/rife-pair/manifest.json
```

The RIFE manifest preserves model/code hashes, input hashes, device settings and every output frame's provenance. `assets/paw-touch/finish-manifest.json` preserves the fixed regions, frame hashes and hold counts. No public feedback or external messages were submitted.
