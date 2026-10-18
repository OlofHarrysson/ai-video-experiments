# Sleeping Presence: ten-second opening

2026-10-18. Olof selected reference B and approved the sleeping presence / slow-awakening direction. This checkpoint tests the first ten seconds only. The remaining minute is not generated or locked.

## Direction and mechanics

The face stays asleep while its surroundings begin to move. Four staggered regional curls turn small lava pockets at the lower centre, lower right, left edge and right edge. Their radii are 0.075–0.11 image heights; total local turns are 55–75 degrees in alternating directions. No curl is centred on the face. These are smooth coordinate fields, not object masks, and their falloff is not a hard exclusion boundary.

A forward approach, sideways drift and slight bank develop together over approximately two delivery seconds, then continue without a stop. Two composed Hermite continuations give zero initial velocity and acceleration. The motion-only preflight measured camera speed at the central pivot rising from effectively zero to approximately 1.15 px/s at 0.5 s, 4.58 px/s at 1 s, and 9.22 px/s at 2 s at the native 1024-pixel image height. Other points move at different speeds because scale and roll also contribute. This verifies the authored camera onset, not the perceptual onset of diffusion reshaping. The final composition and combined motion still require playback judgment.

Curls precede the global transforms in the mapping so their locations follow the overall camera move. No travelling bend, perspective tilt, extra detail pass, reference adapter or pixel copyback is used in this opening.

## Focused opening checks

All cases start from the exact selected 1536×1024 PNG, keep the same seeds and authored motion, and use the established Krea 2 Turbo recurrent initialization, three Euler updates and CFG 1. The first two candidates stop after six new paintings (about 0.8 seconds including the opening). They are preserved, not discarded.

| Case | Change | Assistant observation on native early paintings |
| --- | --- | --- |
| v001 | Original scene/material prompt; noise 0.60 in the tested prefix | Face, horns and sun remain recognizable, but the lava and relief become duller and flatter. Not extended. The configured later noise ramp was never reached. |
| v002 | Same prompt, noise 0.72 | Changing noise alone does not restore material fidelity; broad surfaces remain matte and the fine architecture simplifies. Not extended. |
| v003 | Noise 0.72; revised concrete glass-rib, inlay and reflection descriptions | Clearer specular edges and fine ornament around the brow and cheeks. The face becomes glossier and more stylized than the source, with some simplified surrounding architecture. Selected for the ten-second motion checkpoint. |

The first painting comes from built-in image generation and the repaints from Krea. The first handoff visibly reinterprets details; this is not an exact still-preservation method. The revised prompt improves the early material treatment relative to the two rejected prefixes, not necessarily relative to every detail in the original reference. These observations are specific to this artwork and seed sequence.

Exact configurations and prompts: [v001](opening-v001.json), [v002](opening-v002.json), [v003](opening-v003.json). The selected reference and both original image-generation prompts are preserved in [references](../references/README.md).

## Reproduction and evidence

Run from `apps/deforum` with the project environment:

```sh
uv run --locked python projects/red-rite/experiments/film.py render projects/red-rite/experiments/opening-v003.json --deployment PATH_TO_OWNED_POD_CLIENT
uv run --locked python projects/red-rite/experiments/film.py check projects/red-rite/experiments/opening-v003.json
uv run --locked python projects/red-rite/experiments/finish.py rr-sleeping-presence-opening-v003 pair
uv run --locked python projects/red-rite/experiments/finish.py rr-sleeping-presence-opening-v003 full
uv run --locked python projects/red-rite/experiments/finish.py rr-sleeping-presence-opening-v003 tail
uv run --locked python projects/red-rite/experiments/finish.py rr-sleeping-presence-opening-v003 check
```

Source time is 45 seconds at 24 fps with painting cadence 12. Delivery uses every painting at 4.5× speed: 90 paintings and 240 displayed frames at 24 fps, including the selected still. RIFE synthesizes in-betweens outside the feedback loop. The final interval uses the planned spatial warp instead of an appended static hold. All source paintings, warped inputs and executed ComfyUI graphs are retained under `exports/v001/`; session lifecycle and hash inventories are under `work/red-rite-opening/`.

The original reference prompt record initially contained only metadata despite documentation claiming exact prompts. Both complete strings were recovered from the original image-generation tool call and verified against the two asset keys. Workflow incident: AF-20261018-160629.

## Delivered result and screening

[Open the ten-second film](http://localhost:3028/red-rite). Selected MP4: `exports/v001/rr-sleeping-presence-opening-v003/faster/rife-moving-tail/preview.mp4`. The remaining fifty seconds are pending human review of this opening.

The assistant inspected the original and native paintings at source frames 12, 24, 72, 156, 432, 684 and 1068 across the three tests; the first two cases were rejected at the six-painting checkpoint. The final export was screened with eight overview samples and every displayed frame in 0–0.25 s, 6–6.25 s and 9.75–9.9583 s. The earlier four-second checkpoint also includes every frame from 1.75–2 s. Sheets, timestamps and original extracted frames are retained under `exports/inspection-*`.

The face, horns and eclipse stay recognizable; the eyelids remain closed. The image becomes a glossy black mask with concentric red ornament. Around it, lava lines and paths change while small towers grow and simplify. The broad face keeps clean reflections, but the original intricacy is not fully retained: tiny buildings become fewer, simpler, increasingly tan structures, and the lava has flatter graphic bands. The first 0.125-second handoff is a visible material/geometry reinterpretation, even though the authored camera starts gently. It is the main quality reservation before a longer film. No gross doubled face or disappearance of the eclipse was seen in the sampled windows; that does not establish flawless motion at every timestamp or a human playback preference.

All 90 paintings are retained in the 240-frame export. The final two frames use actual spatial movement, with no appended hold. This is one continuous recurrent passage, with no inserted cuts. The local reviewer certifies all 90 painting positions. Server HTTP 200, original-media byte-range 206 and matching bytes were checked after Terminal Manager restart. No browser interaction was tested or claimed; the established player UI is unchanged.

## Preservation and cost

[Execution receipt](execution-opening.json): 101 generation jobs total, comprising 89 selected repaints and 12 rejected-prefix repaints. All 1,462 remote files were hash-verified locally before deleting the owned Pod and its 202 verified ComfyUI input/output duplicates. The existing model volume remains. Estimated GPU compute cost is **$0.51**, excluding storage, based on the $0.89/hour rate and Pod lifetime. This is an estimate, not an itemized invoice. Both alternative clips, all original stills, all unique paintings and their execution receipts remain available locally.

Ruff passed for the new runners and route file; the three media-server tests passed. The actual generation checks validated each graph, prompt ID, parent image, warped input, output hash and embedded PNG graph. Finishing checked retained paintings, frame timing, dimensions, duration and the moving tail. Human playback and taste judgment are pending.
