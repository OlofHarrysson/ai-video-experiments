# Preservation controls with the current Krea recipe

Plan recorded before rendering, 2026-09-13. Olof authorizes parallel research and bounded experiments around low noise, samplers, reference conditioning and nearby initial noise. Three research agents own separate source-backed notes; the main agent owns shared GPU resources, inference submission and integration. Stay within the existing $10 session budget; target at most $1.50 for this round, with approximately $2.67 previously estimated. Preserve the retained model volume and archive all owned outputs before cleanup.

## First controlled comparison

Start each branch from the exact canyon-city painting used by the correlated-noise experiment. No motion or prompt switch, so background changes cannot be attributed to a warp or changed text. Four seconds, 24 fps delivery, four new paintings per second; shared opening plus fifteen recurrent updates. Each update initializes from that branch's previous RGB output. Use Krea Turbo, CFG 1, incrementing seeds 918273 onward, and RIFE 4.25 scale 1 only for finishing. The final quarter-second holds the last painting.

- Euler, starting sigma 0.60: fresh matched control; compare against the previous control's saved paintings to establish cross-session repeatability rather than assuming it.
- Euler, literal starting sigma 0.10 and0.20: proportionally scale all nonzero sigmas from `[0.6,0.512844085693,0.310901075602,0]`. These are not the older ComfyUI denoise-fraction settings. Keep three descending intervals.
- VAE-only recurrence: encode/decode and save each output using the same PNG feedback. This is a reconstruction control, not a diffusion film or a candidate for interesting morphing.
- Heun 0.60 audition selected after research: same sigma points, but five model evaluations rather than Euler's three. Do not add ancestral randomness merely because it is available.

Reference-image conditioning and nearby opening-noise demonstrations will be specified after research establishes an executable, minimal comparison. Keep input initialization and optional reference conditioning explicit; no inversion or replacement of the recurrent loop is authorized by these experiments.

Inspect every source painting in contact sheets, matched full-size detail crops and selected consecutive delivery frames. Report roof/window retention, palette/shading, crispness and temporal changes separately. Image-difference metrics describe changes, not aesthetic quality. Surface only the clearest comparisons to Olof; preserve all attempts and make the other videos selectable in the local reviewer.

Research outputs: [sampler practices](../../../../../docs/research/krea-sampler-practice.md), [reference conditioning](../../../../../docs/research/krea-reference-continuity.md), [low-noise diagnosis](../../../../../docs/research/krea-low-noise-diagnostics.md).

## Results and viewing

**Euler with literal starting noise 0.1 is the strongest preservation candidate here.** It holds roofs, towers and arch identities much better than 0.6, while losing some surface modeling and metallic richness. This is a stationary holding test, not evidence that 0.1 can make an interesting scene transition. Keep the accepted filmmaking recipe while reviewing these diagnostics.

[Open the synchronized reviewer](http://localhost:3028/). Default: current 0.6 versus 0.1; all other completed videos remain selectable. Each video is four seconds, 1536×1024, 24 fps, sixteen anchors including the shared opening, seventy-five RIFE intermediates and five final hold frames. Every branch retains its own recurrent generated state. No motion or changing text was used.

| Comparison | Observed result | Decision |
|---|---|---|
| [Euler 0.6](../exports/continuity-controls-v001/euler-060/section-016/rife/preview.mp4) | Replaces roof caps, spires, supports and small buildings; apparent framing evolves without a programmed move. | Matched baseline for the unwanted-redraw problem. |
| [Euler 0.1](../exports/continuity-controls-v001/euler-010/section-016/rife/preview.mp4) | Much better silhouette/layout retention, with simpler patina and weaker gold highlights. | Best holding candidate; material flattening remains. |
| [Euler 0.2](../exports/continuity-controls-v001/euler-020/section-016/rife/preview.mp4) | Similar structure retention but more tonal simplification and detail changes. | No clear advantage over 0.1 in this scene. |
| [Heun 0.6](../exports/continuity-controls-v001/heun-060/section-016/rife/preview.mp4) | Different roof/window replacements; no clear preservation improvement. | Keep Euler. Warm recorded jobs were 6.78s versus 4.46s, about 1.52×. |
| [VAE-only](../exports/continuity-controls-v001/vae-only/section-016/rife/preview.mp4) | Retains conspicuous highlights, but develops wavy railings, boundaries and distant fine edges. | Reconstruction itself can degrade detail; its pattern differs from low-noise repaint flattening. |

The original 0.6 trajectory reproduced all sixteen previous independent-noise paintings pixel-for-pixel using new prompt IDs. This checks reproducibility; it is not another independent seed trial. Lower normalized adjacent RGB differences at 0.1 agree with the visual retention, but pixel metrics do not rank aesthetic quality. Heun uses five model evaluations across the same three intervals; Euler uses three.

### Related probes

- [Extra reference image](reference-screen.md): three new one-repaint probes plus the reused current baseline isolate encoder, style adapter and added reference. The reference restores some vehicles lost by the adapter alone, but offers no clear overall preservation improvement over baseline. Stop this particular branch after the screen. This does not rule out other reference methods.
- [Opening noise](noise-openings.md): five independent openings test an exact replay, nearby actual noise and independent noise, with the same prompt and full eight-step recipe. These openings are separate from the recurrent video comparisons.
- [Clean-latent control](continuity_latent.py): fifteen sigma 0.1 repaints after a single VAEEncode, with each sampled latent feeding the next sampler. First decoded painting matches the RGB branch exactly. Sixteen actual latent files and per-cycle images are archived. Direct latent feedback retains more source-like gold coloring, while RGB becomes redder; both still lose metallic highlights, and the latent result has no overall contrast advantage. [Matched latent video](../exports/continuity-latent-v001/cycles-15/section-016/rife/preview.mp4) and [review sheets](../exports/continuity-review-v001/review-verdict.md) are available; all 96 delivery frames and sixteen anchors are verified. This isolates repeated reconstruction at the current recipe; it does not implement latent-space spatial motion.

### Evidence and limits

[Independent source/delivery review](../exports/continuity-controls-v001/assistant-review.md) covers every source anchor through contact sheets, matched native crops, every first-pair frame and selected consecutive late delivery frames. Both 0.6 variants still have softened/doubled small outlines during RIFE transitions. This is frame-sequence inspection, not a claim that every delivered frame was visually reviewed. One scene and seed sequence cannot establish a universal optimum or diagnose distillation as the cause.

All 75 main jobs passed source/parent hashes, requested/executed graphs, uploaded-path substitution, prompt IDs and successful recorded histories. All five videos fully decode; every preserved anchor and output-frame hash matches the finishing manifests. Local archive verification additionally covers remote input/output bytes. HTTP upload acknowledgements alone did not contain input checksums; the separately downloaded remote-media archive supplies those bytes for later inspection.

### Resources

This task completed 84 jobs: 60 main diffusion repaints, 15 reconstruction controls, 15 latent-chain repaints in one job, 3 reference probes and 5 opening probes. That is 83 generated diffusion images plus 15 reconstructions; duplicate SaveImage exports are not additional model evaluations. All 1,536 archive files are local and SHA-256 verified. The owned RTX4090 Pod, 217 owned remote media files, scratch directory, temporary recorder node and the downloaded style adapter were removed; the authorized model volume remains. Estimated cost is **$0.40**, including a $0.02 disk allowance, not posted billing. This estimate excludes the other task's concurrent saved-state/history experiments and retained-volume recurring storage.
