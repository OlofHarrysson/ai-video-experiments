# Lower clean-reference influence

2026-10-12. Olof rejects the strength-1 reference clips as too static and warm for the film. He requests a smaller one-world test of lower reference influence and rules out using the opening image as a fixed reference for now. The broad shapes surviving is not sufficient creative success. Mode collapse is a proposed explanation, not an established diagnosis.

## Frozen comparison

`reference-weights.json` contains two tidal branches at `ref_boost=0.5` and `0.2`. They inherit the original moving reference case unchanged apart from case name and this single control. Reuse the preserved `nr-move-tidal-reference` (1.0) and `nr-move-tidal-baseline` controls. Each new branch has seventeen new paintings, eighteen including its original, and two seconds of eventual 24-fps delivery. No city, second seed, fixed-opening reference, masks, refinement, altered prompting or sampling changes are included.

The clean reference remains the branch's own previous painting after camera movement. Initial noise is 0.72; the exact three-update schedule, full scene/material text, preservation instruction, seed sequence, CFG1, resolution, edit adapter strength 1 and image-grounding resolution 768 remain fixed. Lower influence should permit more visual evolution; judge whether that evolution preserves enough recognizable forms and crisp relief without recreating the baseline's jumps.

## What the weight controls

The pinned adapter adds `log(max(ref_boost, 0.0001))` to attention scores from target tokens to clean reference tokens, then attention is normalized. Thus 1 adds no bias, 0.5 adds about -0.693 and 0.2 adds about -1.609. This changes the relative attention assigned to that reference. It is not a pixel blend, a fraction of the input image, or a calibrated amount of flicker. `ref_boost_a` applies to earlier references only in multi-reference mode and is inactive for our single reference. The grounded image/text path and learned adapter remain active at both tested values; lowering this weight is not equivalent to removing all reference conditioning.

[Pinned source implementation](https://github.com/lbouaraba/comfyui-krea2edit/blob/86f886dac23013d88996e3a2e99093ba44d322fb/__init__.py) · [Author usage notes](https://github.com/lbouaraba/comfyui-krea2edit/tree/86f886dac23013d88996e3a2e99093ba44d322fb).

## Results and review

[Compare the two new clips with the usual repaint](http://localhost:3028/world-seed-reference-weight). The earlier weight-1 reference is retained in the selector. Both new clips are two seconds, eighteen paintings and 48 displayed frames. No candidate is selected as a clear visual improvement; human judgment of these two clips is pending.

- **0.5:** looks close to weight 1. Surface changes differ slightly, but major forms remain similarly restrained while warming and smooth, pitted simplification accumulate.
- **0.2:** allows more local redesign. The lower-left crescent develops a ring beginning around painting 3 (about 0.33s delivery), and a small extra orb appears above the large planet around painting 6 (about 0.67s). These changes persist. The larger scene still largely follows the same forms, and native-resolution final surfaces have lost much of the opening's fine grain. Warming remains.

The weight affects the output, but these settings do not provide the desired balance of lively evolution and crisp surfaces. This does not establish that every lower value will fail, or identify a single cause of the recurring degradation. It tests one attention path while the image-grounded language path, full-strength learned adapter and explicit preservation instruction all remain active. Those other influences are separate candidate experiments, not changes made here. Original-keyframe conditioning remains excluded by Olof's direction.

Screening covered every raw painting in both new branches, the complete first RIFE interval, native-resolution samples, and every displayed frame in 0.50–0.75s and 1.50–1.75s windows. The weight-0.5 native images at paintings 1 and 11 were compared with the corresponding weight-1 sources; weight-0.2 final painting was inspected at native size. Overview and dense windows show connected camera motion and local redraws; still-frame screening does not establish the human experience of playback rhythm. The existing baseline and strength-1 records were reused without regeneration.

## Preservation and execution

All 34 new jobs pass exact graph/history, embedded PNG graph, parent-image hash and recomputed-warp checks. The two frozen configurations differ from the earlier reference case only in case name and reference weight; their generated graphs differ only in output filename and that weight. Both final deliveries pass source/interpolation provenance checks. The reviewer validates original source hashes, dimensions, decoding and timestamps; the named route returns 200 and all four media range requests return 206. Three server tests and focused Ruff checks pass.

All 482 remote files (250,914,739 bytes) match local SHA256 and lengths. The queue was empty before removing 68 hash-verified owned input/output duplicates and two temporary node/weight symlinks. The owned Pod is deleted and absent from the Pod list; the retained 50GB model volume remains. Estimated compute is about $0.23, excluding storage. Archives, runtime source/logs and cleanup receipts remain under `work/reference-weight-session/`. The initial runner launch reached ComfyUI before its restart finished and exited without submitting a job; after the service answered, the same frozen runner completed successfully. No generation setting changed during that retry.

[Execution receipt](reference-weights-execution.json). Recheck from `apps/deforum` with `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/reference-weights.json`. The original 196-job study matrix remains unchanged. The local reviewer stays available through Terminal Manager for human inspection.
