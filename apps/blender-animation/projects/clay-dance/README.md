# Side by Side

Two original clay puppets, Pip the ochre dog and Bo the blue rabbit, perform three dance phrases on one locked stage. This is a character-motion study following [Big Softie](../../../stop-motion/projects/big-softie/README.md), with native 3D geometry and authored contacts replacing generated drawing swaps. Olof selected the clay-like 3D direction on 2026-10-01.

## Watch and edit

The selected take is **v004**. Rendering, full video decode, audio levels and frame review are complete; evidence and limits are recorded in [REVIEW.md](REVIEW.md). Human playback preference remains pending.

| Dance | Timing | What changes |
| --- | --- | --- |
| Groove | 0–6 seconds | Planted feet, alternating arm arcs, hip sway, counter-rotating shoulders and delayed head/ears. |
| Side step | 6–12 seconds | Shared out/together/return/together steps, lifted swing feet and hips shifting toward the supporting shoe. |
| Robot | 12–18 seconds | Fast attacks into held angular arm poses and opposing head/chest turns. |

- [Full film](output/v004/delivery/side-by-side.mp4)
- [Groove](output/v004/delivery/groove.mp4), [side step](output/v004/delivery/side-step.mp4), [robot](output/v004/delivery/robot.mp4)
- [Editable Blender scene with packed music](output/v004/clay-dance-editable.blend)
- [Six-second earlier proof](output/v002/proof/proof.mp4)
- [Brief](BRIEF.md) and [review](REVIEW.md)

The 18-second film uses 216 native poses at 12 poses per second, held twice for 432 delivered frames at 24 FPS. The resolution is 1280×720. An original locally synthesized bass, mallet and percussion track runs at 120 BPM. There are no external samples, generated video frames, image interpolation, paid inference jobs or downloaded character assets.

## Tools and ownership

[The app's clay-animation tools](../../tools/README.md) provide persistent puppet meshes, analytic two-link limb posing, native keyframe baking, camera/light/stage construction, versioned rendering and reopened-scene checks. [choreography.py](choreography.py) owns the dance phrases; [build.py](build.py) owns the cast and production settings. [score.py](score.py) creates the original soundtrack. [finish.py](finish.py) preserves native frames, adds labels, encodes the film and individual dances, validates decoding/frame count, and makes pose sheets and hashes.

The native scene contains ordinary parented objects and transform keyframes. It plays without Python handlers, add-ons, network requests or external textures. Select `PIP | stage` or `BO | stage` to reposition a character. `pelvis & chest`, `head`, ear objects and limb objects have baked keys at odd frame numbers. Three timeline markers identify the dances. The root is a stage-placement control; the baked limbs do not follow later chest edits automatically. For coordinated posing, edit the beat-space targets in `choreography.py` and rebuild. The separate handoff file opens on the camera, includes a `START HERE` text and packs the original score into its timeline. The untouched render-source scene remains `clay-dance.blend`.

This is a jointed puppet workflow, not a skinned anatomical character rig or motion-capture system. Feet have explicit contacts; the motions are stylized and hand-authored, without a physics simulation. The current fixed expression and repeated phrases limit acting range.

## Rebuild

Run from the repository root on this Mac, using Blender 5.2.1 LTS, Metal, FFmpeg, and `uv`. The Python scripts declare their small dependencies inline. Choose a fresh version for each new build; existing takes are never overwritten.

```sh
blender -b --python-exit-code 1 --python apps/blender-animation/projects/clay-dance/build.py -- --version v005 --stills 7,153,319

uv run --script apps/blender-animation/projects/clay-dance/score.py apps/blender-animation/projects/clay-dance/output/v005/score.wav

blender -b apps/blender-animation/projects/clay-dance/output/v005/clay-dance.blend --python-exit-code 1 --python apps/blender-animation/tools/check_clay.py -- --motion apps/blender-animation/projects/clay-dance/output/v005/motion.json --output apps/blender-animation/projects/clay-dance/output/v005/scene-check.json

blender -b apps/blender-animation/projects/clay-dance/output/v005/clay-dance.blend --python-exit-code 1 --python apps/blender-animation/tools/render_clay.py -- --output apps/blender-animation/projects/clay-dance/output/v005/final-frames --percentage 100 --samples 48

uv run --script apps/blender-animation/projects/clay-dance/finish.py --version v005

blender -b apps/blender-animation/projects/clay-dance/output/v005/clay-dance.blend --python-exit-code 1 --python apps/blender-animation/projects/clay-dance/handoff.py -- --score apps/blender-animation/projects/clay-dance/output/v005/score.wav --output apps/blender-animation/projects/clay-dance/output/v005/clay-dance-editable.blend
```

For a quick proof, render a short frame range at 50% and 16 samples. `render_clay.py --frames 1,3,5,...` also accepts an explicit list for isolated dance samples. `finish.py --proof` expects exactly two seconds from the start of each of the three six-second sections, in that order; its audio edit uses the matching source ranges.

All takes, native scenes, frame sequences and generated sound live in ignored `output/`. Source snapshots, a pose manifest and delivery hashes accompany the media. A fresh Git clone can reconstruct the procedural assets, unlike the earlier image-dependent dog rigs. Local generated media is not backed up by Git.

The v004 delivery preserves v003's completed groove renders. `assemble.py` verifies the unchanged builder/toolkit and identical opening pose records, copies those 72 images by hash, and joins 144 newly rendered v004 poses. The final frame manifest records each source. A fresh rebuild using the commands above simply renders all 216 poses; the one-time edit script is not needed.

## API references checked

- [Blender animation and rigging](https://www.blender.org/features/animation/)
- [Native property keyframes](https://docs.blender.org/api/current/bpy.types.bpy_struct.html)
- [Current action slots and channel bags](https://docs.blender.org/api/current/info_quickstart.html)
- [Interpolation modes](https://docs.blender.org/api/current/bpy_types_enum_items/beztriple_interpolation_mode_items.html)

Those sources inform Blender integration. The character designs, two-link target solver, choreography and score are authored here.
