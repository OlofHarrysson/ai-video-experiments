# Puppy: hybrid 2D animation

A three-second bow, hop, and landing, delivered at 1920×1080 and 24 FPS. Painted raster artwork is mapped onto deformable 2D meshes in Blender. The 24-bone rig, paw targets, animation curves, and drawing switches remain editable. This is a 2D cutout/mesh workflow, not Grease Pencil stroke animation or a fully redrawn cel sequence.

## Deliverables

- `output/v011/puppy-2d.mp4`: revised neck attachment, head timing, flexible ear, and shorter blinks; 72 native Blender frames, three seconds, H.264.
- `output/v011/before-after.mp4`: synchronized v007/v011 comparison, with the original on the left.
- `output/v011/puppy-2d.blend`: editable scene with all nine required image textures packed into the file.
- `output/v011/frames/`: full-resolution native PNGs and `rig-verification.json`.
- `output/v011/attachment-verification.json`: evaluated artwork silhouette overlap through every frame.
- `output/v011/review-all/`: decoded review images and timestamp metadata.
- `assets/`: all four original image-tool outputs and derived pieces. [Exact prompts and provenance](PROMPTS.md).
- `output/v001/` through `output/v010/`: preserved scenes, pose-review drafts, and earlier deliveries.

Media is local and ignored by Git. The saved final `.blend` contains its own rig and packed artwork. Rebuilding from source additionally requires the preserved local 3D test scene at `../playful-puppy/output/v003/playful-puppy.blend` and the generated sources in `assets/`.

## How the combination works

The earlier 3D body and paw motion is retimed from 30 to 24 FPS. The camera is orthographic and materials emit flat artwork colours. Far legs are offset for a readable profile. The head sits closer to the chest, and the torso's neck extends beneath the jaw with weights blending from the body to the head. A small UV alpha feather blends the open jaw base into that neck. The ear root follows the head; its middle and tip bend separately with delayed recovery. Limb meshes follow upper/lower bones and independently controlled paws.

The folded foreleg drawing replaces the normal drawing on frames 17–28. It is bound from the desired bow pose back into the rig's rest space, allowing it to continue deforming with the skeleton. A separately drawn paw is shared by both variants. The eye drawing replaces only a masked interior region on frames 20–21 and 55–56; the original head silhouette, nose, mouth, and surrounding artwork remain in place. Switches use constant interpolation, with no image crossfade. Newly authored head keys lead the bow and recover after the landing.

The artwork came from four calls to the built-in image tool. Blender authored the movement and rendered every delivery frame; no video generation or optical-flow interpolation was used. Art sources and exact prompts are preserved separately from pose/rig authoring code.

## Build and render

Run from the repository root, choosing a new version to preserve existing scenes.

```sh
uv run --script apps/blender-animation/projects/puppy-2d/prepare_parts.py

blender -b --python-exit-code 1 \
  --python apps/blender-animation/projects/puppy-2d/build_scene.py \
  -- --version v012 --frames 1,16,17,20,29,44,55

blender -b apps/blender-animation/projects/puppy-2d/output/v012/puppy-2d.blend \
  --python-exit-code 1 \
  --python apps/blender-animation/projects/puppy-2d/render_review.py \
  -- --output apps/blender-animation/projects/puppy-2d/output/v012/frames

blender -b apps/blender-animation/projects/puppy-2d/output/v012/puppy-2d.blend \
  --python-exit-code 1 \
  --python apps/blender-animation/projects/puppy-2d/attachment_check.py \
  -- --output apps/blender-animation/projects/puppy-2d/output/v012/attachment-verification.json \
  --minimum-area .005

ffmpeg -hide_banner -loglevel error -framerate 24 -start_number 1 \
  -i apps/blender-animation/projects/puppy-2d/output/v012/frames/frame_%04d.png \
  -frames:v 72 -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart \
  apps/blender-animation/projects/puppy-2d/output/v012/puppy-2d.mp4
```

`build_scene.py` uses Blender's bundled Python. `prepare_parts.py` declares its Pillow dependency for `uv`. `render_review.py` reopens and verifies the scene before rendering. Flat emission materials render on the CPU; v007's 72 final frames took 87.050 seconds on this Mac with Cycles at 16 samples and no denoising.

## Earlier review

Initial pose review exposed a detached tail root, overlapping far-leg attachments, and texture folding in the deep bow. Repositioning the tail/far legs and adding slight mesh depth separation corrected attachments and overlap artifacts. A purpose-drawn folded limb corrected the deep-bend silhouette.

The first replacement changed paw size visibly. Sharing a paw between drawings preserved that shape, but a cropped paw retained an unattractive cut edge. A dedicated isolated paw and corrected wrist landmark removed the cut edge and closed the join. The original whole-head expression swap also changed more artwork than needed; restricting the replacement to the eye region preserved the head design.

Reopening v007 verified all 72 frames, one active foreleg drawing per side, and an always-active base head. Maximum evaluated paw-target error is 0.00080636 scene units; held-bow paw drift on any axis is below 0.000001 units. These measurements check rig control, not complete collision freedom or artistic quality.

The final eight-frame overview and all three dense-review pages were inspected, covering the drawing switches at 0.583334–0.750001 s and 1.083334–1.250001 s, and landing at 2.083334–2.333334 s. The selected images show the bow, airborne pose, landing compression and recovery without the earlier torn elbow or cropped paw stump. The cutout layering remains visible around some joints; the side-view setup and limited expression library constrain acting. These are sampled-frame findings; real-time playback taste remains for Olof to assess.

## Head attachment and motion revision

Olof reported that v007's head was not properly attached and that the animation remained unconvincing. The prior paw checks and sampled review had missed a real silhouette failure: the new texture-aware overlap check finds zero direct head/torso overlap at frame 35. The ear could visually conceal part of the missing neck. This review failure is recorded centrally as AF-20260909-235535.

The revision preserves the same artwork and body/paw action while testing four changes: closer head placement with a deforming neck (v008); independent head timing and a two-segment flexible ear (v009–v010); short blink holds (v010); and a feathered open-jaw join (v011). v009 retained unwanted inherited head keys and was superseded before delivery. All drafts remain local.

`attachment_check.py` rasterizes the evaluated meshes and their texture alpha in the picture plane. It reads the saved material's jaw feather when present, and reports direct head/torso overlap per frame. This checks contact independently of the ear; it does not establish correct anatomy, invisible seams, or attractive motion. The full render must also be inspected.

v011 was reopened and rendered at 1920×1080, 24 FPS, with 72 distinct native frames. Maximum paw-target error remains 0.00080636 scene units and held-bow drift remains below 0.000001. At 120 check pixels per scene unit, minimum head/torso overlap is 2,711 pixels (0.18826 square scene units) at frame 11; v007 had zero overlap on frames 35–44. The check includes v011's jaw alpha feather.

All 72 decoded frames were inspected on six 12-frame review pages, with full-resolution checks of the bow, airborne pose, landing recovery, and comparison export. The neck stays connected in this action, and the open jaw base blends into the chest. The ear flex and head timing vary independently of the body. Foreleg drawing switches and sharp knee bends still reveal the cutout construction; the short blinks also retain a slight difference in the painted eye region. These are frame-review findings, not a claim of release-quality character animation or a substitute for Olof's playback judgement.

`delivery.json` records decoded video metadata, frame uniqueness, rig/attachment metrics, and media hashes. Both delivery videos contain 72 decoded frames and run for exactly three seconds. v011's native render finished in approximately 81 seconds on this Mac. No new image generation or paid compute was used for this revision.
