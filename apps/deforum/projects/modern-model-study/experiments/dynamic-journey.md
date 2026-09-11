# A faster journey through changing scenes

Status: prepared; GPU execution blocked by RunPod startup/capacity on 2026-09-11. **No new diffusion paintings or finished video were generated.** Olof says the previous films are good and likes the umbrella-to-jellyfish morph, but isolated changes between similar objects are too limited. The next film needs changing environments and compositions, quicker pacing and sustained movement.

## Creative test

Build approximately 24 seconds: a short preserved watch-to-snail opening, then travel into a towering brass city, through a submerged garden, past floating cloud palaces and out into a cosmic landscape. Success requires recognizable changes in the surroundings and viewing scale, not merely new ornament on a fixed central subject. Retain the recurrent warped-image initialization throughout. No independent scene redraw or substituted text-to-image frame is authorized by this scene-change request.

First render a short scene-change probe from the same saved snail painting at two repaint strengths. If the environment changes convincingly, continue the promising branch in short reviewed sections. If it does not, refine that transition before rendering the whole duration. New motion phrases overlap and reverse direction rather than ending in several static seconds. Preserve every attempt; show one recommended complete film, with an alternative only if meaningfully different.

## Recipe and boundaries

- Krea 2 Turbo, three Euler sampling intervals, CFG 1, changing reproducible seeds. Test proportional sigma schedules with larger brief transition pulses; lower the noise again while a scene develops.
- 24 fps delivery; a diffusion painting every 0.5s and eleven RIFE intermediate images. RIFE stays outside generation. Every delivered painting remains in order.
- Time-based Lanczos warps, using composed bounded twist/zoom/translation phrases. Same API graph and model weights as the preceding session; no new model or custom ComfyUI node.
- Reuse the previous opening through 3.5s, branching from `ten-dollar-v001/clock-pulse/anchors/0084.png`. New scene prompts target the entire setting and viewpoint. A shared anchor joins the old opening to the new continuation.
- Keep the combined work within the original $10 allowance. The preceding Pod's posted bill is now **$0.174271** (compute plus disk). Reserve at least $1 of the remainder; this session may spend at most **$8**. Reuse the retained model volume when capacity permits, archive and verify results, then delete owned compute. Keep the authorized model cache.

## Evidence

The initial cached-region allocation remained `initializing / awaiting_container` for approximately fourteen minutes. Requested RUNNING status did not establish readiness; MCP logs timed out or returned empty and the CLI returned no system lines. Startup diagnosis is recorded as AF-20260911-233120. No model inference ran, no files were uploaded, and the actual startup cause remains unverified. The owned allocation was deleted and an empty Pod list confirmed cleanup. Subsequent RTX 4090, A100, A40 and alternate-host PRO 4500 allocations were rejected as unavailable, including a CLI check; the catalog's Low stock did not establish that a matching Pod could be rented.

The failed startup's estimated compute exposure is approximately **$0.17 plus disk**, based on the $0.72/hour quote and allocation duration. Its billing query returned no posted records yet; this is not evidence of zero cost. The retained 50 GB model volume was verified present. No new GPU or additional storage resource remains.

Local validation checked exact inversion of composed motion maps at phrase boundaries, actual full-resolution RGB warps, the matching inherited join image, and the stationary final tail. A six-sample motion-only sheet was inspected; it is a geometric diagnostic, not new generated artwork. Independent source review found no blocker in recurrent initialization, half-second painting spacing or the 3.5-second prefix join. Remote inference and actual output quality are still untested.

Record configurations, exact prompt/motion/noise schedules, per-painting lineage, short section reviews, final timing and budget/cleanup receipts alongside the outputs. Olof's playback assessment will determine whether the result is sufficiently dynamic; assistant frame screening is preliminary evidence.

## Resume

Runner: [dynamic_journey.py](dynamic_journey.py); local finishing: [dynamic_journey_finish.py](dynamic_journey_finish.py). The immutable [gentler](dynamic-journey-configs/gentler.json) and [bolder](dynamic-journey-configs/bolder.json) configurations differ only in transition starting noise: 0.72 or 0.84, each returning to 0.64 after the initial transition phase. Neither is a selected recipe yet. Preserve the existing Krea graph and three proportional sampling intervals.

1. Follow [the Pod runbook](../../../POD.md), checking actual allocatable capacity and all currently owned resources. Replace the stale private deployment receipt with the newly owned Pod. The prepared upload bundle and archive/restore scripts are under ignored `work/dynamic-journey-session/`; no secrets are included in the bundle. The source painting is already copied to `exports/dynamic-journey-v001/source/seed.png`.
2. On the ready Pod, from the app directory, run `python projects/modern-model-study/experiments/dynamic_journey.py projects/modern-model-study/experiments/dynamic-journey-configs/gentler.json --deployment work/dynamic-journey-session/deployment.json --through 4`, then the same command with `bolder.json`. Use the verified ComfyUI virtual environment, not system Python.
3. Download both probes, inspect the paintings and first interpolated pair, then choose/refine the scene transition. Continue the selected case through 10s and 15s for review, then omit `--through` to complete its 20.5-second continuation. Existing receipts are resumed without duplicate generation.
4. Locally, run `dynamic_journey_finish.py CASE --stage prepare`, then `pair`; inspect the first-pair video before `full`. Finally `join` preserves the original 3.5-second prefix and every new painting in a 576-frame / 24-second film. All five motion phrases have settled before its final half-second hold. Use the repository Python environment with NumPy, Pillow and OpenCV; the finisher calls the existing pinned RIFE environment.
5. Archive and verify every generated input, output and receipt before removing owned remote files and deleting the Pod. Keep the retained model volume. Update this note from the actual scene changes, not the intended prompts.
