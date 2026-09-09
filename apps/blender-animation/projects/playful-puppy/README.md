# Playful puppy

Three seconds of native character animation: notice, play bow, gather, hop, land, settle. The original sculpted puppy has a continuous skinned coat, a 23-bone rig, four independent paw controls, head motion, articulated tail, moving ears, and blink shape keys. No generated image assets, generative video, or optical-flow interpolation are used.

## Files

- `build_scene.py`: model, materials, skeleton, skin weights, key poses, animation curves, camera and lights.
- `render_review.py`: reopen the saved scene, measure paw control error over all 90 frames, and render through Cycles on Metal.
- `output/v003/playful-puppy.blend`: editable scene; local, ignored by Git.
- `output/v003/frames/`: final native 1280×720 frames at 30 FPS, Cycles 32 samples with denoising.
- `output/v003/puppy-bow-hop.mp4`: final delivery.
- `output/v003/frames/rig-verification.json`: per-frame target and evaluated paw positions, measured after reopening the saved scene.
- `output/v001/` and `output/v002/`: preserved earlier scenes and review renders. The v002 draft uses every second native frame at 15 FPS.

## Authoring and rendering

Run from the repository root. Choose a new version/output folder to preserve previous scenes and media.

```sh
blender -b --python-exit-code 1 \
  --python apps/blender-animation/projects/playful-puppy/build_scene.py \
  -- --version v004 --frames 1,26,55,69

blender -b apps/blender-animation/projects/playful-puppy/output/v004/playful-puppy.blend \
  --python-exit-code 1 \
  --python apps/blender-animation/projects/playful-puppy/render_review.py \
  -- --output apps/blender-animation/projects/playful-puppy/output/v004/frames --samples 32

ffmpeg -hide_banner -loglevel error -framerate 30 -start_number 1 \
  -i apps/blender-animation/projects/playful-puppy/output/v004/frames/frame_%04d.png \
  -frames:v 90 -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart \
  apps/blender-animation/projects/playful-puppy/output/v004/puppy-bow-hop.mp4
```

For a smaller draft, render with `--step 2 --percentage 60 --samples 16`; encode the resulting glob at 15 FPS. This samples the same animation at lower frequency, without interpolating pixels.

Open the `.blend` in Blender, select `BISCUIT | pose controls`, and use Pose Mode. `ROOT` controls travel/height; `BODY` controls torso pitch; `HEAD`, `ear.*`, and `tail.*` control secondary movement. `CTRL.paw.*` sets paw positions and orientations. Timeline markers identify the action beats. The named action is `Biscuit | bow, hop, settle`.

## Review and revisions

The v001 pose renders exposed belly deformation spikes from overly broad leg weights, partially buried decorative patches, a detached blink highlight, and insufficient jump headroom. The v002 pass localized the limb envelopes, simplified the coat details, fixed the blink deformation, widened framing, and tucked the legs more at the jump apex.

The reopened v002 scene exposed a maximum paw-target error of 0.0984 scene units during takeoff. V003 adds earlier forepaw lift, explicit flight and descent keys, and a smaller recovery overshoot. Its maximum error over all 90 frames is 0.00092745 units; held-bow paw drift on any coordinate axis is below 0.000001 units. These validate control fidelity, not artistic quality or complete mesh collision freedom.

The first Metal render incurred about 109 seconds of startup/compilation before its first frame. Subsequent v002 draft frames took roughly 1.4 seconds. V003 final frames take roughly 2.9 seconds on this Mac. These are local observed timings, not a general performance guarantee.

Visual review uses the shared `apps/deforum/video_review.py` harness. Sampled pose and dense transition sheets are evidence for silhouettes and deformation; they do not independently establish how satisfying real-time playback feels. The final is a motion/authoring proof with a simple sculpted appearance, not the earlier anime film's finished art direction. Minor shoulder pinching and the segmented paw design remain limitations of this procedural asset.

Final delivery verified: 90 distinct PNG frames, each 1280×720; H.264 MP4 decodes to 90 frames at 30 FPS and exactly 3.000 seconds. All final overview samples and every-frame windows at 1.50–1.70 s and 2.066667–2.333334 s were visually inspected. The bow, lift, airborne silhouette, forepaw-first landing, compression, and recovery are visible in those samples, without the earlier belly spike or detached eye highlight. Real-time playback preference remains for Olof to assess. `output/v003/delivery.json` records media hashes and encoding/render settings. Final rendering took 260.683 seconds; no render process was left running.
