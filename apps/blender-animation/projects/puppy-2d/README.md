# Puppy: hybrid 2D animation

A three-second bow, hop, and landing, delivered at 1920×1080 and 24 FPS. Painted raster artwork is mapped onto deformable 2D meshes in Blender. The 23-bone rig, paw targets, animation curves, and drawing switches remain editable. This is a 2D cutout/mesh workflow, not Grease Pencil stroke animation or a fully redrawn cel sequence.

## Deliverables

- `output/v007/puppy-2d.mp4`: 72 native Blender frames, three seconds, H.264.
- `output/v007/puppy-2d.blend`: editable scene with all nine required image textures packed into the file.
- `output/v007/frames/`: full-resolution native PNGs and `rig-verification.json`.
- `output/v007/review-overview/` and `review-transitions/`: decoded review images and timestamp metadata.
- `assets/`: all four original image-tool outputs and derived pieces. [Exact prompts and provenance](PROMPTS.md).
- `output/v001/` through `output/v006/`: preserved scene and pose-review drafts.

Media is local and ignored by Git. The saved final `.blend` contains its own rig and packed artwork. Rebuilding from source additionally requires the preserved local 3D test scene at `../playful-puppy/output/v003/playful-puppy.blend` and the generated sources in `assets/`.

## How the combination works

The earlier 3D motion is retimed from 30 to 24 FPS. The camera is orthographic, materials emit flat artwork colours, and the rig's out-of-plane head, ear, and tail rotations are replaced with motion in the picture plane. Far legs are offset for a readable profile. The torso has a small head/neck deformation influence; limb meshes follow upper/lower bones and independently controlled paws.

The folded foreleg drawing replaces the normal drawing on frames 17–28. It is bound from the desired bow pose back into the rig's rest space, allowing it to continue deforming with the skeleton. A separately drawn paw is shared by both variants. The eye drawing replaces only a masked interior region on frames 19–25 and 53–57; the original head silhouette, nose, mouth, and surrounding artwork remain in place. Switches use constant interpolation, with no image crossfade.

The artwork came from four calls to the built-in image tool. Blender authored the movement and rendered every delivery frame; no video generation or optical-flow interpolation was used. Art sources and exact prompts are preserved separately from pose/rig authoring code.

## Build and render

Run from the repository root, choosing a new version to preserve existing scenes.

```sh
uv run --script apps/blender-animation/projects/puppy-2d/prepare_parts.py

blender -b --python-exit-code 1 \
  --python apps/blender-animation/projects/puppy-2d/build_scene.py \
  -- --version v008 --frames 1,16,17,20,29,44,55

blender -b apps/blender-animation/projects/puppy-2d/output/v008/puppy-2d.blend \
  --python-exit-code 1 \
  --python apps/blender-animation/projects/puppy-2d/render_review.py \
  -- --output apps/blender-animation/projects/puppy-2d/output/v008/frames

ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 \
  -i apps/blender-animation/projects/puppy-2d/output/v008/frames/frame_%04d.png \
  -frames:v 72 -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart \
  apps/blender-animation/projects/puppy-2d/output/v008/puppy-2d.mp4
```

`build_scene.py` uses Blender's bundled Python. `prepare_parts.py` declares its Pillow dependency for `uv`. `render_review.py` reopens and verifies the scene before rendering. Flat emission materials render on the CPU; v007's 72 final frames took 87.050 seconds on this Mac with Cycles at 16 samples and no denoising.

## Review and corrections

Initial pose review exposed a detached tail root, overlapping far-leg attachments, and texture folding in the deep bow. Repositioning the tail/far legs and adding slight mesh depth separation corrected attachments and overlap artifacts. A purpose-drawn folded limb corrected the deep-bend silhouette.

The first replacement changed paw size visibly. Sharing a paw between drawings preserved that shape, but a cropped paw retained an unattractive cut edge. A dedicated isolated paw and corrected wrist landmark removed the cut edge and closed the join. The original whole-head expression swap also changed more artwork than needed; restricting the replacement to the eye region preserved the head design.

Reopening v007 verified all 72 frames, one active foreleg drawing per side, and an always-active base head. Maximum evaluated paw-target error is 0.00080636 scene units; held-bow paw drift on any axis is below 0.000001 units. These measurements check rig control, not complete collision freedom or artistic quality.

The final eight-frame overview and all three dense-review pages were inspected, covering the drawing switches at 0.583334–0.750001 s and 1.083334–1.250001 s, and landing at 2.083334–2.333334 s. The selected images show the bow, airborne pose, landing compression and recovery without the earlier torn elbow or cropped paw stump. The cutout layering remains visible around some joints; the side-view setup and limited expression library constrain acting. These are sampled-frame findings; real-time playback taste remains for Olof to assess.
