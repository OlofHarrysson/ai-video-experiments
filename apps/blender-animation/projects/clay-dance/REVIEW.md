# Clay dance review — 2026-10-01

## Question and baseline

Can persistent articulated characters, explicit shoe contacts and beat-timed poses make a more controllable dance study than sparse generated cels? Big Softie's dense nuzzle experiment recorded contour/color drift and difficulty obtaining reliable intermediate drawings. That finding supports trying a different control method; it does not establish that 3D looks better than the painted film.

Olof explicitly selected clay-like 3D characters. The new work preserves Big Softie and the existing Blender dog films.

## Iterations

- **v001:** Six rendered pose checks. Original geometry and staging looked coherent in inspected stills. The side-step foot order narrowed the shoe spacing enough to risk overlap. Corrected before motion rendering.
- **v002:** Fixed side-step ordering, stronger robot poses, blinks, and a visible raised stage. Rendered a six-second proof, two seconds per dance, at 640×360. Inspected twelve poses from each phrase. The two-hands-forward robot pose obscured parts of the face, and the side step lacked an explicit shift toward the supporting foot.
- **v003:** Added support-directed hip shifts during foot lift and moved the raised robot hands to either side of the head. Inspected revised stepping and robot stills before starting the 1280×720, 48-sample render.
- **v004:** Full-size stepping frames revealed crowding between the inward-moving characters' arms. Both now step in the same direction, preserving partner spacing. Rendered four new stepping checks before proceeding. Preserved the unchanged groove renders and stopped the superseded v003 render; its partial output remains intact. The explicit assembly receipt checks matching source code and groove poses, then hashes every reused frame.

All earlier scenes, stills and the v002 proof are preserved. No failed or unique generation was deleted.

## Scene checks

The saved v004 handoff was reopened in Blender 5.2.1 LTS and evaluated at all 216 authored poses. `output/v004/handoff-check.json` records:

- Zero error between authored shoe targets and evaluated shoe positions.
- Zero movement between consecutive planted samples within a dance.
- Minimum shoe-bottom height: 0, on the stage surface.
- Minimum left/right shoe-center distance: 0.680 stage units; shoe width is 0.390.
- Projected mesh bounding boxes remain within approximately x=0.184–0.824 and y=0.154–0.858 of the image.
- The two characters' world-X mesh bounds remain disjoint, with a minimum gap of 0.027 stage units. This is a conservative mesh-box check; it does not imply a large visual gap.
- The packed soundtrack's bytes match the original WAV by SHA-256 after reopening.

The first spacing check required an arbitrary 0.040-unit clearance, which the robot's extended-arm pose did not meet despite positive separation. The retained failed check records that result; the final check tests the intended property, non-intersection of the character bounds. The older v003 inward-step scene fails even that criterion, independently corroborating the visual crowding concern.

The analytic solver rejects unreachable targets instead of stretching a limb. These checks cover target placement, shoe separation and framing; they are not a general mesh-collision test, balance simulation or perceptual-quality score.

## Delivery

The selected v004 delivery is complete:

- Full movie: 1280×720, H.264, 24 FPS, 432 frames, exactly 18.000 seconds; stereo AAC at 48 kHz.
- Three excerpts: each 1280×720, 24 FPS, 144 frames, exactly 6.000 seconds, with stereo AAC audio.
- All four videos passed a complete FFmpeg decode and frame-count check, with zero-start video timestamps.
- Final encoded audio measures −18.7 dBFS mean and −1.5 dBFS peak; no clipping was detected by that sample-level check. This is not a true-peak measurement or listening judgment.
- All 216 native pose PNGs were checked for dimensions and valid decoding. The first 72 retain the verified v003 groove images; 144 are newly rendered from v004. `final-frames/manifest.json` records the lineage and hashes.
- Inspected twelve native poses per dance, revised full-size stepping and robot frames, a full-size blink, and sixteen decoded delivery frames spanning the opening, both sides of each cut, blinks, raised hands and ending. Evidence is under `delivery/*-poses.jpg` and `decoded-review/`.
- Labels change at exactly 6 and 12 seconds. The study uses deliberate cuts between routines, without trying to disguise them as continuous choreography.

`delivery/delivery-check.json` contains full-film metadata and source hashes. `decoded-review/checks.json` contains all four video checks and their hashes. `handoff-check.json` verifies the reopened, music-packed editable scene. The source render and separate editable handoff are both preserved.

Full-film SHA-256: `43e27620e2b55725f60ecbdf6b4c51c83552fb7d2b0aa0de73d0f1ecccca9ddf`.

## Assistant assessment and limits

The inspected sequences have stable character identity and distinguishable movement patterns: a planted sway, travelling steps and held arm accents. The earlier generated-cel contour changes are absent because geometry remains fixed. This changes both rendering style and animation method, so it is not a controlled aesthetic comparison with Big Softie.

The segmented limbs are deliberately visible. Faces mostly retain one expression, and six-second sections repeat short phrases. The approach is suitable for further authored motion tests; it does not yet demonstrate nuanced acting, complex turns, contact between characters or cloth/body deformation. Human playback, soundtrack listening and preference remain pending. Frame inspection and technical decode checks must not be reported as continuous viewing or listening.
