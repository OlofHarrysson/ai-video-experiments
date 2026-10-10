# Opening ten seconds

## Question

Can a richly detailed alien jungle sustain purposeful continuous movement and reveal a materially different world within ten seconds?

## Scope

Three independently generated starting stills establish contrasting worlds for the planned 30-second film. Produce and screen the opening ten seconds before the next human checkpoint. Current film recipe is preserved. RunPod uses standing account-funds authorization; preserve outputs and remove owned compute afterward.

## Acceptance

Detailed, readable starting composition; visible destination; varied overlapping camera motion; an actual transformation/reveal; 240 delivered frames at 24 fps; verified painting provenance and local preservation. Taste remains for Olof.

## Results

Created a silent **10.000-second, 240-frame, 24 fps, 1536×1024** checkpoint at `../exports/cuts/v001/preview.mp4`. [Play in the reviewer](http://localhost:3028/world-seed). Three full-resolution independent stills establish the planned worlds; [contact sheet](../exports/world-stills.jpg).

The final cut uses 70 jungle/passage paintings and 23 independently initialized city paintings, with an eight-frame editorial dissolve beginning at frame 179 (7.458 s). The two finished source passages preserve their own original paintings and interpolation manifests. The dissolve composites the overlapping source frames; it is not an inferred continuous camera crossing. No RIFE is applied across the edit. Both source passages have moving tails.

### Direction and screening

- The original jungle painting supplies an actual root bridge and flower doorway. A 2.1× approach banks toward its measured center over the first three seconds.
- At source frame 312, the oval is centered and still open. A stronger push expands its rim into ornamented black/gold ribs.
- At frame 552, the generated passage curves, leaving a narrow bright exit on the right. The final move is replanned from this painting, carrying incoming velocity into a lateral turn and counter-bank. The unrendered remainder of the previous plan is preserved in its config.
- The first city trial loses the crystal identity and fine detail early. The selected trial keeps the complete opening description and raises repaint noise from .59–.63 to .70–.72. Sampled comparisons support better crystal identity and some richer relief; the two changed variables are not separately tested.
- The assembled overview shows green/violet jungle, coral petals, black/gold architecture and the city reveal. Every displayed frame across 7.375–7.875 s was inspected: the dissolve has expected brief double exposure, then resolves to the independent city shot. A city interpolation window at 1.0–1.25 s and the first interpolation pair were also screened.
- **Assistant reservation:** microscopic detail becomes smoother and more graphic during recurrence. This is a useful story/palette checkpoint, not evidence that the requested higher visual-quality bar is achieved. Human taste feedback is pending. The opening remains mostly forward travel; broader lateral movement and a pullback belong in the remaining twenty seconds.

### Verification and preservation

All three openings and all rendered portions of the five motion cases pass generation/provenance checks: requested/executed graphs, embedded PNG metadata, prompt IDs, parent and warp hashes, exact warp pixels and saved prefixes. Both selected RIFE passages pass finishing checks, preserving source-painting hashes and timing. The final cut passes a complete decode, dimension, duration and frame-count checks; its assembly plan and source hashes are saved beside it. Reviewer server tests: 3 passed. Browser playback reached frame 239 / 9.958 s; seeking back to frame zero worked. The complete uncropped image and controls fit the browser viewport. The local reviewer remains running for Olof at `http://localhost:3028/world-seed`. Perceptual screening used extracted overview/dense frames; browser checks prove playback and seeking, not continuous visual assessment of every frame.

All **116 generated paintings** are preserved locally, including the 22 new paintings of the unused city trial and the reserved crystal still. Original generated media is ignored by Git; no external media backup is configured. After comparison against local hashes, 229 duplicate cloud input/output files (448,781,240 bytes) were removed. Owned pod `efyslvztdx1vcu` was deleted; subsequent pod list was empty. Shared model volume `vd3jnbwko1` remains. Estimated compute **$0.53**, using creation-to-deletion elapsed time at $0.89/hour; not an invoice. [Session record](session.json).

### Continue from here

The planned thirty-second storyboard is in the project README. Review the ten-second cut before extending. The city passage `c02-city-detail`, frame 264, and crystal still `o1-crystal`, frame 0, are the preserved starting points. Keep the three styles materially distinct; do not imply that the saved crystal still is already animated. Address texture retention if this is below Olof's requested detail bar.

### Reproduction

Run from `apps/deforum/`. Configurations are immutable per case; new creative choices need new cases. `film.py` uses shared `deforum_lab` mechanics and stores all run evidence under the project. `finish.py` uses the existing local RIFE runtime. `assemble.py` takes the two selected `faster/rife-moving-tail/preview.mp4` files and `--version v001`, refusing to overwrite an existing cut. Cloud execution needs a new owned deployment; the session's pod is deleted.
