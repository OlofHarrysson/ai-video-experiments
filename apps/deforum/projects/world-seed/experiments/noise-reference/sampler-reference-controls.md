# Lower-noise samplers and reference controls

2026-10-12. Olof approves 0.60 Euler versus 0.60 Euler ancestral at eta 0.25, alongside the preserved 0.72 Euler control, with the editing adapter off. He finds the prior 0.01 reference clip promising and wants to keep exploring it, while still objecting to color drift. This human preference supersedes the earlier assistant decision not to shortlist that clip. Mode collapse remains an explanation to investigate, not a demonstrated mechanism.

## Frozen comparison

[sampler-reference-controls.json](sampler-reference-controls.json) records four branches of seventeen generated paintings, plus the shared opening. Each delivers two seconds at 24 fps with the established 4.5x source-clock conversion and RIFE finishing. The opening hash, detailed prompt, camera, per-painting seed trajectory, CFG1 and dimensions remain fixed. Each branch feeds back its own output.

| Branch | Starting noise | Sampler | Reference boost | Edit adapter strength | Grounding resolution |
| --- | ---: | --- | ---: | ---: | ---: |
| Existing reference-free control | 0.72 | Euler | off | off | off |
| nr-sampler-tidal-euler060 | 0.60 | Euler | off | off | off |
| nr-sampler-tidal-ancestral060 | 0.60 | Euler ancestral, eta 0.25, s_noise 1 | off | off | off |
| Existing promising 0.01 reference | 0.72 | Euler | 0.01 | 1 | 768 |
| nr-ref-tidal-edit050 | 0.72 | Euler | 0.01 | 0.5 | 768 |
| nr-ref-tidal-ground384 | 0.72 | Euler | 0.01 | 1 | 384 |

The 0.60 schedule is exactly 0.600000000000, 0.512844085693, 0.310901075602, 0. The ancestral branch uses ComfyUI's native flow-aware implementation; it injects new noise on the two non-final transitions, with a clean final step. The initial seed is identical at each matching painting index; recurrent input canvases diverge after the first repaint. Its seeded stochastic stream and pinned implementation define the added draws; individual random tensors are not exported.

The reference branches use only the already-warped previous painting. No masks, original-opening reference, copyback, refinement or second artwork are included. Neither new reference branch also changes the sampler. Grounding resolution changes the image information supplied to the vision-language encoder, not a calibrated image-conditioning weight. Halving the LoRA strength scales the learned model-weight adjustment; it does not halve all reference influence.

## Evidence and limitations

Sampler screening is complete: all eighteen source paintings, both native midpoints/finals, each complete first RIFE interval, and every displayed frame in 0.50–0.75s and 1.50–1.75s. Both 0.60 branches preserve the main planet; both turn its lower crescent into a more complete orb/reflection and simplify the original fine grain. The ancestral branch changes some folds, holes and spire bases differently, but provides no clear detail or retention improvement in this trajectory. Both remain cooler than the earlier 0.01 editing-reference clip. No obvious doubled major silhouette appears in the screened interpolation windows. These observations do not establish normal-speed playback preference. [Compare samplers](http://localhost:3028/world-seed-samplers).

The half-strength adapter branch keeps the main planet but broadens foreground spires into stepped hollow cones and later rounds their tips. It is less amber early than the archived 0.01 recipe, then still warms. A small additional moon appears around paintings 9–11 and fades across 11→12 (about 1.21–1.33s); the main planet remains. The full 1.00–1.375s window is inspected as well as the standard intervals. Larger shell holes and cleaner outlines do not establish recovered material grain.

The 384 grounding branch also retains the main planet, but still develops strong amber color and smoother surfaces with enlarged round shell markings. All eighteen paintings, the native midpoint/final, first interpolation interval and both standard dense windows are screened. It is not shortlisted as a color/detail improvement.

The fresh same-GPU 0.01 control also preserves the main planet, warms and simplifies. Two sky points become extra small planets by the end. Its shell markings differ from the earlier GPU's clip; the latter remains preserved as the human-liked version. The same-GPU comparison supports a narrower conclusion: adapter strength 0.5 reduces some amber treatment but also changes shell holes and spire geometry more. It is the more useful new variation to show, not a demonstrated cure for fine-detail loss. Grounding 384 is not selected. Keep the earlier promising 0.01 recipe available and continue treating color, geometry and fine grain as separate criteria. No new production recipe is selected. [Compare reference controls](http://localhost:3028/world-seed-reference-controls). These short, one-scene trajectories can identify useful candidates and failure modes; they do not establish general best settings or sustained thirty-second behavior. The former RTX PRO 4500 is unavailable. New branches share an L4 at $0.59/hour; historical controls used the 4500. The direct new Euler/ancestral comparison holds hardware fixed. A fifth branch, [nr-ref-tidal-control001-l4](reference-controls-hardware.json), repeats the promising 0.01 recipe unchanged on this L4 before interpreting the reference tweaks. This adds seventeen paintings, giving 85 new paintings total. The requested historical 0.72 Euler control is reused; small differences against it cannot be attributed exclusively to settings.

The runner's defaults were checked against the previous committed implementation for every painting in all 42 historical cases. New sampler graphs contain no editing nodes; each new reference graph differs from the 0.01 recipe only at its designated control and output name. All 85 jobs pass the runtime checks: exact executed graphs, PNG metadata, successful histories, parent hashes and camera warps.

Primary sources: [native ancestral node](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py#L452-L469), [flow sampler](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L215-L240), [Identity Edit author guidance](https://huggingface.co/conradlocke/krea2-identity-edit/blob/89e9e7a09ee2e5c9331e952063d79b1b8a703280/README.md).


## Delivery, preservation and resources

All five two-second, 48-frame deliveries pass the finisher and reviewer provenance checks. Browser playback reaches frame 47 at 1.958s for all three sampler clips and the selected reference pair. Both pages are left with two clips selected and paused at the opening. The review pages return 200 and all seven selected/available original-media range requests return 206. All 1,205 remote files, 639,163,236 bytes, are hash-verified locally. The queue was empty before removing 170 verified owned Comfy input/output duplicates and two temporary node/model links. The owned L4 Pod was deleted and its absence verified; the authorized model volume remains. Estimated compute is $0.49, excluding retained storage.

A transfer watcher stopped at the renderer handoff; the completed files were retrieved without rerendering, and full manifest verification passed before cleanup. Runtime source, logs, per-case archives and cleanup receipts remain under `work/sampler-reference-controls-session/`. [Execution receipt](sampler-reference-controls-execution.json).

Recheck from `apps/deforum` with `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/sampler-reference-controls.json`, then the same command with `reference-controls-hardware.json`. The local Terminal Manager reviewer remains running for Olof's inspection.
