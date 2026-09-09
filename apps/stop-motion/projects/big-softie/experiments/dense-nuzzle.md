# Dense nuzzle drawing test

## Result

The image-generation pass produced twenty reviewed candidates; eleven were selected alongside the existing opening drawing. The target of roughly thirty reliable distinct drawings was not met. Small requested movements often became larger changes, requested intermediate poses often resembled the later reference, and repeated repainting increased orange saturation and changed texture.

The selected twelve poses form a two-second nuzzle at six pose exposures per second. A separate local RIFE 4.25 pass inferred ninety-nine intermediate frames, producing sixty frames per second. This is a tenfold increase in frame cadence through interpolation, not tenfold more independent image-generated drawings. The 120-frame sequence contains twelve original anchors, ninety-nine inferred frames and nine final holds.

The delivered four-second comparison adds a half-second opening hold and a one-and-a-half-second ending hold to each version. Both sides use identical drawings, timing and placement. This isolates interpolation. The main nineteen-and-a-half-second v3 film remains the release candidate; this silent motion study does not replace it.

- [Side-by-side comparison](../renders/dense-nuzzle-comparison.mp4): 1920×1080, 60 fps, 240 frames.
- [Clean interpolated clip](../renders/dense-nuzzle-60fps.mp4): 1280×720, 60 fps.
- [Drawing-only clip](../renders/dense-nuzzle-drawings.mp4): six pose exposures per second in a 60 fps container.
- [Exact generation prompts and parent references](dense-nuzzle-generations.json).

## Drawing workflow

Olof requested substantially more actual animation drawings and suggested reviewing each result before choosing the next. The opening was `assets/source/settle-e.png`; `assets/source/settle-g.png` supplied an eventual destination reference. A fixed park plate lets character motion be judged without background drift.

First, sequential edits attempted small head movements, followed by cheek contact, a puppy blink, an adult nod and an adult blink. Every result was inspected. Original artwork was reintroduced as a color reference when saturation drift appeared. Next, adjacent accepted poses were supplied together to request missing intermediate positions. These requests did not reliably produce the intended fractions of motion. Rejected candidates were preserved but excluded from the final sequence.

The selected order is `000, 001, mid01, 002, 003, b34, 004, 005, b56, 006, 007, 009`. Selection follows observed pose progression rather than generation order. The built-in image tool did not explicitly report its routed model variant. Generated backgrounds were opaque; the existing alpha-extraction tool prepared the cels, with every original retained.

All twenty original generations live under `assets/source/dense-nuzzle/`; extracted frame copies and interpolation inputs live under `assets/dense-nuzzle/`. The JSON prompt record identifies originals, prepared frames, parents and selection. These media folders are ignored by Git and remain local.

## Finishing and review

The existing repository RIFE runner uses the author's 4.25 weights and pinned Practical-RIFE code (`bbfd2ea90910789a860ea3e2b32a240cd577b75e`). A first-pair render was reviewed before the full sequence. The full interpolation completed locally on MPS in 17.45 seconds; no cloud resources were used.

The interpolated head and eyelid transitions are more gradual in the inspected intervals. Color and texture drift remain visible because interpolation carries changes between the source drawings. More files and higher output fps do not establish convincing acting or consistent artwork. A longer film should not scale this particular image-editing recipe without improving motion spacing and repaint stability.

Validation:

- All twelve anchor PNGs match their input composites byte for byte.
- All ninety-nine inferred frames have distinct hashes and differ from their adjacent endpoints.
- Reviewed the first pair, an evenly spaced full-sequence overview, every frame in the adult-nod window, and selected full-size frames.
- HyperFrames strict checks passed without findings, and the strict render completed successfully.
- Both final exports decoded without errors. The comparison has 240 frames at 60 fps and a four-second duration.

Evidence is under `review/dense-nuzzle/`, including `check-final.json`, `render-final.log`, `probe-final.json`, contact sheets, and `comparison-final.jpg`. The interpolation directory includes a manifest with frame classification and provenance. These are assistant frame inspections and technical checks; human playback preference remains unconfirmed. The nose-region statistic in `review-dense.mjs` is only a rough dark-pixel diagnostic, not a reliable tracked landmark.

## Reproduce from preserved artwork

From the project directory:

```sh
node scripts/prepare-dense-rife.mjs
```

From `apps/deforum/`, using its existing local environment and model:

```sh
work/rife-session/.venv/bin/python interpolate.py ../stop-motion/projects/big-softie/assets/dense-nuzzle/rife-input ../stop-motion/projects/big-softie/assets/dense-nuzzle/rife-first-pair --source-frames 12 --source-fps 6 --multiplier 10 --pair-only
```

Review the first pair before running the full sequence:

```sh
work/rife-session/.venv/bin/python interpolate.py ../stop-motion/projects/big-softie/assets/dense-nuzzle/rife-input ../stop-motion/projects/big-softie/assets/dense-nuzzle/rife-60fps --source-frames 12 --source-fps 6 --multiplier 10 --validated-pair ../stop-motion/projects/big-softie/assets/dense-nuzzle/rife-first-pair/manifest.json
```

Back in the project directory:

```sh
ffmpeg -v error -framerate 6 -i assets/dense-nuzzle/rife-input/%06d.png -vf 'fps=60,tpad=start_duration=0.5:stop_duration=1.5:start_mode=clone:stop_mode=clone' -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart renders/dense-nuzzle-drawings.mp4 -y
ffmpeg -v error -i assets/dense-nuzzle/rife-60fps/preview.mp4 -vf 'tpad=start_duration=0.5:stop_duration=1.5:start_mode=clone:stop_mode=clone' -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart renders/dense-nuzzle-60fps.mp4 -y
node scripts/build-dense-review.mjs
npx hyperframes@0.8.33 check assets/dense-nuzzle/composition --strict --snapshots --at 0,0.8,1.3,2,2.5,3.9 --json
npx hyperframes@0.8.33 render assets/dense-nuzzle/composition --quality high --fps 60 --workers 2 --strict-all --output renders/dense-nuzzle-comparison.mp4
```
