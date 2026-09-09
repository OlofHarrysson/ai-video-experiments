# A Little Brave

A 16-second native Blender film: Biscuit, a hesitant golden puppy, meets Bruno, a much larger Rottweiler. A ball offered in play turns their first meeting into a gentle greeting.

The film uses two persistent painted 2D rigs, authored foot contacts, a rolling ball, three camera shots, and an original piano/celesta score. Image generation supplies still artwork. Blender supplies all 384 animation frames; no image-to-video model or generated intermediate frames are used.

## Local deliverables

The current finishing candidate is `film-v007`; its 1920×1080, 24 FPS, 128-sample native render is in progress. Earlier full cuts and every draft remain preserved. Delivery verification will be recorded after encoding.

| Item | Local path |
| --- | --- |
| Editable film | `output/film-v007/a-little-brave.blend` |
| Neutral character stage | `output/characters-v001/characters.blend` |
| Biscuit collection asset | `output/characters-v001/biscuit-asset.blend` |
| Bruno collection asset | `output/characters-v001/bruno-asset.blend` |
| Eight reusable pose actions | `output/poses-v001/character-actions.blend` |
| Pose settings and image index | `output/poses-v001/presets.json`, `manifest.json` |

The film packs 19 images, one font, and one soundtrack. The neutral stage and individual character assets pack their own artwork. Media is ignored by Git and retained locally; rebuilding from a fresh clone requires these local assets or the packed Blender files.

## Working with the characters

Open `characters.blend` for an unanimated stage, or append `01 Biscuit` / `02 Bruno` from the individual asset files. Both collections are marked as Blender assets. Each has a stage-placement empty and a 24-bone armature. The saved viewport opens in material preview; enable overlays to see the bones, then select an armature and enter Pose Mode.

| Control | Purpose |
| --- | --- |
| Stage-placement empty | Position, scale, or mirror the whole character in a scene |
| `ROOT` | Move the torso while the independent paw targets hold their positions |
| `BODY`, `HEAD` | Pose the body and head around their drawn joints |
| `CTRL.paw.*` | Place the four feet; two-bone inverse kinematics bends the legs |
| `ear.near`, `ear.far`, `ear.tip` | Ear movement and delayed tip motion |
| `tail.01`, `tail.02` | Tail arc and follow-through |
| Armature property `closed_eyes` | Switch to the smiling closed-eye drawing |
| Armature property `folded_forelegs` | Switch to the foreleg drawings made for a play bow |
| Bruno's `HEAD` properties `gaze_x`, `gaze_y` | Move the iris within its native eye aperture |

In `character-actions.blend`, select a rig and choose one of its named actions in the **Action Editor**. These single-frame actions include both bone poses and drawing properties. They were verified by assigning each action after reopening the file. The separate neutral stage is preferable when starting a new performance from scratch.

The artwork is designed for a side view. Moving the camera around the dogs does not reveal a fully modeled character, and extreme poses need additional drawings or a redesigned mesh. This is a controllable cutout animation workflow.

## Authoring and rendering

Run commands from this directory. Blender 5.2.1 LTS and FFmpeg are installed locally; standalone Python tools use `uv`. Every scene/render command requires a new version or output folder to preserve previous results.

```sh
blender -b --python-exit-code 1 --python build_film.py -- --version film-v008 --frames 1,125,250,384
blender -b output/film-v008/a-little-brave.blend --python-exit-code 1 --python render_film.py -- --output output/film-v008/preview-frames --percentage 50 --samples 8
blender -b output/film-v008/a-little-brave.blend --python-exit-code 1 --python render_film.py -- --output output/film-v008/final-frames --percentage 100 --samples 128
uv run --script finish.py --version film-v008
```

`build_film.py` uses the previous puppy's `puppy-2d/output/v011/puppy-2d.blend`, Bruno's `output/rottweiler-v004/puppy-2d.blend`, the parked artwork in `assets/`, and `choreography.py`. It archives its authoring sources beside each saved scene. `build_rottweiler.py` and `prepare_parts.py` retain the adult character's construction recipe. `export_characters.py` produces the neutral stage and separate collection assets; `build_pose_catalog.py` extracts reusable pose actions from a film.

`finish.py` verifies all PNGs, encodes H.264/AAC, checks the frame count and audio format, performs a full decode, and records SHA-256 hashes. The full film is 16 seconds at 24 FPS, with 48 kHz stereo audio. The saved film can also play its packed score directly in Blender.

## Review and provenance

- [Brief](BRIEF.md): story, requested working time, and quality criteria.
- [Review](REVIEW.md): inspected versions, defects, revisions, checks, and remaining limits.
- [Exact still-art prompts](PROMPTS.md): all seven generation calls and preserved outputs.
- `scripts/score.swift`: original local piano/celesta composition, adapted from the earlier Big Softie experiment and rendered with Apple's system instrument bank. The film uses no borrowed movie soundtrack.

The source puppy is preserved in the neighboring `puppy-2d` project. The exploratory blink deformation and Biscuit gaze tests remain in this project; they are not used in the selected film.
