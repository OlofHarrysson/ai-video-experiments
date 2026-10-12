# Adapter strength and deterministic sampler follow-up

2026-10-12. Olof prefers editing strength 0.5 because color drift is reduced. He approves exploring more strengths and two additional samplers on the same artwork. This preference applies to the reference experiment, not a replacement of the selected full film.

## Frozen comparison

[Matrix](adapter-sampler-followup.json): six two-second trajectories, seventeen new paintings each (102 jobs). Fresh Euler 0.60 and editing-strength 0.5 controls run on the same GPU as the four variations.

| Branch | Starting noise | Sampler | Editing strength | Reference boost | Grounding |
| --- | ---: | --- | ---: | ---: | ---: |
| nr-ref-tidal-edit050-repeat | 0.72 | Euler | 0.5 | 0.01 | 768 |
| nr-ref-tidal-edit025 | 0.72 | Euler | 0.25 | 0.01 | 768 |
| nr-ref-tidal-edit075 | 0.72 | Euler | 0.75 | 0.01 | 768 |
| nr-sampler-tidal-euler060-repeat | 0.60 | Euler | off | off | off |
| nr-sampler-tidal-heun060 | 0.60 | Heun | off | off | off |
| nr-sampler-tidal-dpmpp2m060 | 0.60 | DPM++ 2M | off | off | off |

All branches retain the warped previous painting as diffusion initialization. The full material prompt, opening, camera, seed trajectory, CFG1, three sigma intervals and 1536x1024 output stay fixed. Each branch recurs through its own generated paintings. Reference branches also receive the clean warped previous painting through the existing edit path. Only the editing weight delta changes; the 0.01 attention bias and image-grounded prompt path stay fixed. Sampler branches have all three editing paths off. RIFE finishing stays outside feedback. No masks, fixed-opening reference, copyback, refinement or second artwork.

## Why these samplers

Krea's [official implementation](https://github.com/krea-ai/krea-2/blob/main/sampling.py) uses Euler. Alternatives are hypotheses, not model-author recommendations. The pinned ComfyUI implementation exposes a denoised estimate consistent with Krea's flow velocity. [Heun](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L269-L300) makes a provisional update, evaluates the model again and averages directions on nonfinal intervals. It costs five model evaluations across our three intervals; Euler costs three. Churn is zero, so it draws no fresh noise after initialization.

[DPM++ 2M](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L796-L818) uses successive denoised estimates within each repaint to improve its update. It retains three model evaluations and no fresh step noise. With only three intervals, its multistep correction operates on the middle interval; it has no memory across video paintings. We do not alter its native implementation. Both use the exact same 0.60, 0.512844085693, 0.310901075602, 0 schedule.

An earlier stationary lost-city study found no clear Heun advantage. Repeating it here asks a different, narrower question about the current detailed tidal scene under motion; that previous result is not forgotten or treated as a general prohibition. See [continuity controls](../../../modern-model-study/experiments/continuity-controls.md).

## Evidence

All three adapter trajectories are generated and screened. Both repeated controls reproduce all eighteen prior paintings pixel-for-pixel and both finished pair/full MP4s byte-for-byte. The current comparison therefore reproduces the preferred reference baseline and the earlier Euler 0.60 result, rather than relying only on matching settings.

- **0.25:** cooler than 0.5, but the shell becomes more regular honeycomb and the foreground gains rocks. The original planet persists. A large additional moon grows early and remains; a smaller moon appears around 0.875–1.0s, disappears around 1.08s and later returns. Fine grain still simplifies. Show as the useful alternative, not a proven improvement.
- **0.5:** preserve Olof's preferred balance. The reproduced clip retains the main planet but warms and smooths, with the previously noted transient extra small moon.
- **0.75:** the main planet persists without extra moons observed in these eighteen paintings. Shell folds remain simpler and spires become glossy. Stronger amber coloration and a rust-colored shell exterior return; no convincing fine-detail gain. Available as a preservation/color tradeoff, not the default shortlist.

The two new adapter clips receive complete eighteen-painting overviews, native intermediate/final inspection, all four frames of the first interval and all fourteen frames in 0.50–0.75s and 1.50–1.75s. The 0.25 sky event also receives every frame from 0.875–1.25s. No gross doubled major silhouette is observed in those interpolation windows. This does not establish normal-speed human preference.

**Heun 0.60:** the main planet remains, while its reflection fills into an orb. Scattered dots and orange flecks accumulate, shell folds become wavier, and terrace edges become more graphic. These are additional marks, not convincing retention of the original mineral grain. No clear detail or preservation advantage over Euler is selected. Median warm job execution is 20.352s versus Euler's 12.986s, about 1.57x, excluding the first job in each arm.

**DPM++ 2M 0.60:** the main planet remains, but the shell becomes flatter and more wavy, with dark/rust streaks and more geometric marks. Thin spires develop rounded tips. It is the stronger change in appearance, not a demonstrated fine-detail gain. Median warm execution is 13.104s, close to Euler. Show it beside Euler to make the sampler contrast visible; Heun and the earlier ancestral/0.72 controls remain selectable.

Both new sampler clips receive complete eighteen-painting overviews, native final inspection, every frame of the opening interval and both standard dense windows. Heun painting 6 is also compared directly with Euler. No gross doubled major silhouette is observed in those windows. The repeated Euler delivery is byte-identical to the previously screened clip, including its pair and full moving-tail versions; prior dense-window screening therefore remains applicable.

## Recommendation and limits

Retain editing strength **0.5**, reference boost **0.01**, grounding **768** and ordinary Euler as the preferred reference recipe for this scene. Present **0.25** as the cooler but more inventive alternative. Increasing to 0.75 buys a quieter sky in this trajectory at the cost of more warmth. Neither new sampler beats Euler for the requested material detail in this comparison. Color bias and fine-grain loss remain separate issues: improving one has not solved the other.

This is one scene and one seed trajectory, with 17 new paintings per branch. It does not establish a universal best strength or sampler, stable thirty-second behavior, or human preference for the new clips. No production film is replaced and no sampler/adapter combination or refinement pass is tested. The next useful quality question is whether a separate light detail pass can add genuine surface relief without destabilizing the loop; it remains unrun.

[Compare adapter strengths](http://localhost:3028/world-seed-reference-controls) · [Compare samplers](http://localhost:3028/world-seed-samplers). Each page defaults to two clips; other tested variants remain selectable. The unchanged player is rebuilt from verified full-resolution originals. Both pages return 200 and all eleven original-media range requests return 206. Browser playback is not rechecked in this sprint.

## Verification and resources

The updated runner reproduces every requested historical graph across 47 prior cases. All 102 planned graphs isolate only their designated control. All 102 executed jobs pass exact requested/executed/PNG graph, successful history, source/parent hash, recomputed camera warp and dimensions checks. Six two-second, 48-frame, 1536x1024 deliveries pass finisher and reviewer provenance checks. Focused Ruff checks and all three reviewer-server tests pass.

All 1,446 remote files (801,302,876 bytes) and transfer archives are SHA-256 verified locally. After an empty-queue check, 204 verified owned Comfy input/output duplicates and two temporary links are removed. The owned L4 Pod is deleted and absence verified; the authorized model volume remains. Estimated GPU compute **$0.5612**, excluding retained storage and not a posted-billing figure. [Execution receipt](adapter-sampler-followup-execution.json). Private runtime source, logs, archives and cleanup receipts are under `work/adapter-sampler-followup-session/`.

Recheck from `apps/deforum` with `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/adapter-sampler-followup.json`. The Terminal Manager media reviewer remains running for Olof's inspection.
