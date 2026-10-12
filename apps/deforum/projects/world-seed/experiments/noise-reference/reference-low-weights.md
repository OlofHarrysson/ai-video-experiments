# Very low clean-reference weights

2026-10-12. Follow-up to the [0.5 / 0.2 comparison](reference-weights.md). Olof asks whether 0.05 or 0.01 can reduce the static, warm and smoothed treatment further, and how the reference weight should be interpreted. He also proposes lower starting noise plus smaller noise injections during sampling. The reference sweep and sampler question stay separate.

## Frozen comparison

[reference-low-weights.json](reference-low-weights.json) contains two tidal branches: `nr-weight-tidal-005` at 0.05 and `nr-weight-tidal-001` at 0.01. Each uses seventeen new paintings, eighteen including the shared opening, for a two-second 24-fps delivery. Only case name and `ref_boost` differ from the preceding weight comparison. The existing controls remain preserved and are reused.

The reference is always this branch's previous painting after camera movement. No fixed opening reference, mask, copyback, refinement, prompt change, step change, adapter-strength change or second artwork is included. Full-strength Identity Edit v1.2, image-grounded prompt encoding, CFG1, the exact three-interval 0.72 schedule, camera and seed trajectory remain fixed.

## Meaning of the control

The adapter adds `log(max(weight, 0.0001))` to target-to-reference attention logits. This multiplies the reference's unnormalized attention contribution by the requested factor before normalization. Thus 0.05 and 0.01 are respectively four and twenty times weaker than 0.2 on this direct attention path, with other logits held fixed. They do not specify final-image percentages. At a single attention row, if the reference's original normalized share is `p`, its new share is `weight*p / (1-p+weight*p)`. This is an explanatory calculation, not a measurement of our model's attention. For example, a hypothetical 99% original share would still become about 50% at weight 0.01.

The image-grounded language encoding, preservation wording and learned edit adapter are unchanged. Reference tokens also remain present in the transformer. Reducing this one direct attention path therefore does not switch off every route by which the reference can affect the output. A zero input would be clamped to 0.0001; it is not a true reference-free control. Reducing the LoRA's strength is another possible experiment, but changes learned editing behavior rather than providing a calibrated per-image mixture. No such change is made here.

[Pinned reference implementation](https://github.com/lbouaraba/comfyui-krea2edit/blob/86f886dac23013d88996e3a2e99093ba44d322fb/__init__.py#L129-L157).

## Sampling proposal

The separate [sampling follow-up](../../../../../../docs/research/reference-conditioned-repainting.md#smaller-initial-noise-and-stepwise-randomness--2026-10-12) records the user's proposal and an isolated test design. No sampler modification is included in these reference-weight renders.

## Results

The completed 0.05 branch keeps the large ringed planet and shell through all seventeen repaints, while the shell and terraces become warmer, smoother and more glossy. Early bright sky points develop into two small orbs. The source's lower-left crescent becomes a more complete reflection of the main planet. Source inspection therefore shows both retention and local redesign; it does not show recovered fine material grain. At 0.01 the shell changes more: folds rearrange, round pits become much larger dark holes, and the smaller chambers develop a different spiral. The main planet survives every source painting and its lower reflection becomes more complete. Fine grain still gives way to smooth surfaces and the warmer palette persists. The initial assistant screening did not shortlist either branch as a clear material-fidelity improvement. Olof subsequently finds 0.01 promising and pretty decent, and asks to continue it while addressing the remaining color drift. That human preference guides the next [sampler and reference-control study](sampler-reference-controls.md).

[Compare 0.01, 0.05 and the preceding 0.2 result](http://localhost:3028/world-seed-reference-weight). The 0.5, 1.0 and reference-free controls remain selectable.


## Verification and resources

All 34 new jobs pass exact requested/executed/PNG-embedded graph checks, successful Comfy histories, parent-image hashes and recomputed camera warps. The frozen controls and generated graphs differ from the preceding reference recipe only in case/output name and `ref_boost`. All 482 remote files, 250,479,730 bytes, are verified locally by SHA256 and length. Both two-second, 48-frame RIFE deliveries pass the finisher's source and frame-provenance checks. The reviewer verifies hashes, dimensions and decoded timestamps; the page returns HTTP 200 and all six original-video range requests return 206. No server or generation code changed.

Screening covers every raw painting in both branches, both final native-resolution paintings, every frame in the first interpolation interval, and every displayed frame in the 0.50–0.75s and 1.50–1.75s windows. These show connected camera progression and ongoing local redraws without a missing main planet. They do not independently establish normal-speed human perception of flicker or rhythm. Browser playback reached frame 47 at 1.958s on all three compared clips; the page was then left with the two new clips selected and paused at frame zero. Olof subsequently identifies 0.01 as promising; the other low-weight branch has no stated preference.

The queue was empty before removing 68 hash-verified owned Comfy input/output duplicates and two temporary model/node links. The owned RTX PRO 4500 Pod was deleted and its absence verified. The authorized 50GB model volume remains. Estimated compute is $0.21, excluding retained storage. Runtime source/logs, transfer archives and cleanup receipts are preserved under `work/reference-low-weight-session/`. An early extraction began before its transfer completed and failed the output-hash check; the completed archive was extracted again and all files subsequently passed the full manifest check. No generation was rerun or changed as a result.

[Execution receipt](reference-low-weights-execution.json). Recheck from `apps/deforum` with `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/reference-low-weights.json`. Earlier study matrices and unique media remain preserved. The Terminal Manager reviewer remains available for Olof's inspection.
