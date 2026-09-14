# Recent latent history and gentle noise recurrence

Completed 2026-09-14 local time (2026-09-13 UTC). Olof sees no improvement over the baseline; retain the production recipe.

Approved 2026-09-13. Olof requests a plain explanation of the saved-state experiment, approves the recurrent follow-up, and proposes mixing recent image latents. Test both factors in a matched four-case stationary city study. Hypothesis: a short history could damp incidental redesign, but averaging may soften detail or retain overlapping forms. Mosaic avoidance is unproven.

The previous replay study repeatedly sampled the **same** image latent, perturbing one recorded noise pattern along a small arc. Outputs did not become subsequent inputs. Here every new painting becomes the next input; history cases also include up to two older paintings.

| Case | Noise | Image initialization |
| --- | --- | --- |
| Fresh | Independent each repaint | Latest painting's VAE latent |
| Gentle | AR(1), rho 0.995 | Latest painting's VAE latent |
| History + fresh | Independent each repaint | Recent three image latents, newest first, weights 70/20/10 |
| History + gentle | AR(1), rho 0.995 | Same weighted history |

When fewer than three paintings exist, normalize the available weights. This uses the ordinary VAE encodings of completed RGB paintings, preserving the current encode/decode feedback path in all cases. It does not average random noise with clean latents or copy protected pixels over the result. Raw history states, mixed initialization and actual noise are archived per repaint.

Noise is `epsilon_i = rho epsilon_(i-1) + sqrt(1-rho²) eta_i`, with native seeded Gaussian innovations 918273..918287. At rho 0.995 the fresh innovation coefficient is approximately 0.10, substantially smaller than the earlier rho 0.85 test. Initial noise is identical across all four cases. Starting sigma remains 0.6 with three Euler intervals, CFG 1, same Krea Turbo/model hashes, unchanged city text and no warp.

Run four first-painting controls and require pixel-identical parity with each other and the archived correlated-noise study. Then complete fifteen repaints per case: four paintings/s, four seconds at 24 fps including the common opening. Review raw paintings/holds first, without RIFE; finish with the established RIFE only if it helps assess a promising case. A history benefit with a stationary unchanged scene does not establish usefulness during motion or prompt transitions; historical latents would need spatial correspondence under motion.

Keep the original production recipe. Use one short-lived RTX 4090 and the retained model cache, initially bounded below $1 within the remaining authorized budget. Preserve every output, verify lineage and hashes, and delete only owned resources. Other active experiments and their reviewer default remain untouched.

## Findings

| Case | Assistant review |
| --- | --- |
| Fresh | Retains bronze shading but changes roofs, towers and distant architecture over successive repaints. All fifteen outputs reproduce the earlier independent-noise control pixel-for-pixel. |
| Gentle | Develops bright mosaic-like surface markings and saturated colors despite the smaller noise-pattern changes. This misses preservation. |
| History + fresh | Keeps more of the foreground roof layout and scene structure near the opening, but towers and small details still change. No clear reduction in individual repaint jumps. |
| History + gentle | Still develops the mosaic style. The tested latent-history blend does not prevent the effect. |

Inspection covers matched paintings at 0/1/2.25/3.75 seconds, consecutive paintings 12–15, and a native roof crop before/during/after RIFE interpolation at 3–3.25 seconds. Both finished variants retain soft or doubled fine edges in that sampled interval. History does not freeze exact structures or establish smooth semantic transformations.

For fresh noise, history reduces final-versus-opening normalized RGB mean absolute difference from 0.10877 to 0.08768 (about 19% lower). However, mean consecutive-painting change is almost identical: 0.03992 versus 0.03987. These are pixel-difference summaries, not validated flicker or quality scores. They support a distinction between reduced accumulated drift and reduced per-repaint variation; they do not establish a perceptual improvement on their own.

The fixed-source replay result therefore did not generalize to preservation under gently evolving noise recurrence. Keep fresh independent noise for the preservation goal. The tested history blend has no demonstrated visual advantage worth adopting. Motion and deliberate prompt changes remain untested and may expose alignment problems or delayed transformations.

## Human feedback — 2026-09-14

Olof sees no significant improvement, or any improvement, over the baseline. The assistant agrees: reduced accumulated drift did not translate into a convincing improvement in smoothness or image quality. Earlier 'promising' framing gave too much weight to that diagnostic measurement. Keep the baseline and park these tested history/correlated-noise recipes for preservation. Preserve the mosaic result as a possible stylistic option, not a continuity solution. This feedback update adds no inference.

## Outputs and inspection

[Open the dedicated reviewer](http://localhost:3028/history-recurrence). It defaults to latest-painting feedback versus recent-latent history, both using fresh noise and identical RIFE 4.25 scale 1 finishing. All four raw variants remain selectable. Sixteen paintings including the opening occupy the same timestamps in each four-second, 96-frame, 24 fps clip; fifteen new diffusion paintings occur at 0.25–3.75s. RIFE adds five intermediate frames between paintings and holds the final painting for the remaining frames. Interpolation never feeds back into generation.

- [Fresh + RIFE](../exports/history-recurrence-v001/fresh/section-016/rife/preview.mp4) and [history + fresh + RIFE](../exports/history-recurrence-v001/history-fresh/section-016/rife/preview.mp4).
- Raw: [fresh](../exports/history-recurrence-v001/fresh/raw/preview.mp4), [gentle](../exports/history-recurrence-v001/gentle/raw/preview.mp4), [history + fresh](../exports/history-recurrence-v001/history-fresh/raw/preview.mp4), [history + gentle](../exports/history-recurrence-v001/history-gentle/raw/preview.mp4).
- [Overview](../exports/history-recurrence-v001/overview.jpg), [late consecutive paintings](../exports/history-recurrence-v001/late-consecutive.jpg), [native RIFE roof crop](../exports/history-recurrence-v001/rife-detail.jpg).

The local reviewer was browser-checked at 1280×720: both complete images and shared controls fit without scrolling, Shift+Right reaches painting 1/frame 6 in both panels, linked playback shows matching interpolation labels, and both end at frame 95/final painting 15. This is a playback/layout check, not a guarantee of permanent decoder-level frame locking.

## Verification and resource closure

All 60 unique jobs completed. Executed graphs and parent/history image hashes verify genuine recurrence. Actual saved tensors verify the 70/20/10 mixture, normalized startup weights, noise statistics and rho 0.995 recurrence using the same innovations as the fresh-noise branches. Older encoded latents match their earlier recorded encodings exactly. All four first repaints are pixel-identical; all fifteen fresh-control paintings match the archived prior control. See [generation check](../exports/history-recurrence-v001/generation-check.json).

All 1,129 remote archive files passed local SHA256 verification, including every generated painting and the actual noise, component-history and mixed-input tensors. Four raw videos fully decode with certified painting/hold labels. Both RIFE finishes retain all sixteen anchor paintings pixel-for-pixel and fully decode: [raw delivery check](../exports/history-recurrence-v001/delivery-check.json), [RIFE check](../exports/history-recurrence-v001/rife-check.json).

Owned Pod `t2aj1t5470qlv3` was deleted; deletion was confirmed by listing. Its 300 owned remote media/tensor files, scratch and experimental node were removed after verification. The retained 50 GB model volume was preserved. Estimated cost is **$0.25**, including a disk allowance; this is not posted billing and excludes concurrent task costs.

A suffix-based resume lookup matched two case names after parity. No duplicate inference occurred. Exact per-anchor receipts now resume completed paintings with graph and hash checks; future run names are distinct. The workflow lesson is recorded centrally as AF-20260913-235531. This patch leaves the generic helper unchanged for unrelated studies.

## Reproduction

Use [history_recurrence.py](history_recurrence.py) stages `prepare`, `parity`, `render`, with an owned Pod deployment receipt. The experimental [history/noise node](../../../history_noise.py) imports the existing noise sequence helper. It uses VAE encodings of completed paintings, not retained sampler-output latents. The current controlled test has no spatial warp.

After restoring the archive, [history_recurrence_review.py](history_recurrence_review.py) stages `verify` and `media` audit the executed jobs and build raw reviews. RIFE uses the existing `dynamic_journey_finish.run(case, stage)` helper with `finish.d.OUT` set to this study's output directory, stages `pair` then`full`, for `fresh` and `history-fresh`. Build the [saved review session](../../../media_review/sessions/history-recurrence.json) with `media_review.py` into `media-review-history-recurrence-v001`.
