# Intermediate descriptions for a changing scene

Status: completed 2026-09-13. Both videos and all generated artifacts are verified locally; Olof’s initial feedback is promising but inconclusive (see below). Olof accepts a test of intermediate scene descriptions and describes it as a kind of prompt interpolation. This study uses discrete descriptive stages, not embedding blending.

Compare two 6.5-second continuations from the same saved brass snail painting. Both use the [higher-peak noise curve](transition-ramps.md): 0.40 → 0.78 across six paintings, then a smooth three-painting return to 0.64. Preserve the same Krea model, seeds, three Euler sampling intervals, CFG 1, half-second repaints, bounded Lanczos motion, 24 fps and RIFE 4.25 scale 1. The final half-second holds the native last painting after spatial motion settles.

| Case | 0.5–1s paintings | 1.5–2s paintings | 2.5–6s paintings |
| --- | --- | --- | --- |
| direct | Canyon city | Canyon city | Canyon city |
| bridges | Brass snail shell inhabited by small buildings | Hollow spiral pavilion surrounding a city passage | Exact same canyon-city description as direct |

Intermediate prompts describe the visible image, keeping the final prompt's material, lighting and style language. They do not issue next-frame editing commands or change the opening image. Exact text is frozen in the [runner](prompt_bridges.py) and generated configurations. No automatic prompt expansion, image blending, regional protection or new conditioning nodes are added.

The recurrent runner's optional `prompt_schedule` selects text independently of its existing scene/noise schedule. Text changes must not restart the noise ramp. Local checks compare every repaint's sigmas with the previous higher-peak configuration and verify the prompt changes at 1.5s and 2.5s, while checking unchanged legacy behavior.

Hypothesis: descriptive intermediate states can make the shell-to-city transition more legible and give RIFE smaller structural changes to bridge. Risks: explicitly describing the shell may prolong its dominance; changing the text in stages may still produce abrupt repaint changes. Judge painting progression first, then matched interpolated windows. Keep the previous result as a reference and render a fresh direct control in the same runtime as bridges.

Execution used these two cases (24 new paintings), with all inputs/outputs and receipts archived before deleting the owned Pod. The authorized model cache remains. This round's cap was $2 within the original $10 session budget. Prior successful sessions total $1.6060 posted, plus the earlier $0.25 startup allowance. Human preference remains unconfirmed until playback feedback.

## Results

Videos: [intermediate descriptions](../exports/prompt-bridges-v001/bridges/section-013/rife/preview.mp4) · [direct city prompt](../exports/prompt-bridges-v001/direct/section-013/rife/preview.mp4). Both are 6.5 seconds at 24 fps with identical RIFE settings.

The intermediate descriptions change the path of the transformation, but do not establish a clear smoothness improvement. Keep the direct prompt as the default pending Olof's playback feedback; staged text remains a useful option when a particular hybrid form is wanted.

| Time | Direct city prompt | Intermediate descriptions |
| --- | --- | --- |
| 0.5–1.5s | The snail remains largely intact; a distant skyline and marks inside its spiral begin to appear. | More rectangular openings and architectural bands appear on the shell. They are not clearly miniature inhabited buildings at contact-sheet scale. |
| 2s | Architectural ribs develop around a largely solid center. | A small aperture and a more explicit radial architectural cavity develop. |
| 2.5s | A broad city passage replaces much of the shell and desert foreground. | A thick, ribbed architectural shell surrounds the passage: the clearest hybrid stage. |
| 3–6s | A clear canyon city develops around the inherited circular frame. | The inner ribs give way to a similar open city, retaining a patinated metal rim and denser terraced buildings on the right. |

Both still make their largest structural replacement between 2 and 2.5 seconds. The staged branch then clears more of its inner shelving between 2.5 and 3 seconds. It supplies a legible hybrid, without proving that the total change is distributed more evenly. Neither case escapes the inherited circular framing; both retain useful depth, overlapping arches and shadows while later surfaces become more illustrative.

Main review inspected all 26 paintings and sampled first-pair interpolation frames. The [independent painting review](prompt-bridges-independent-review.md) also finds a clearer shell/building hybrid but recommends retaining direct, because the principal repaint jump remains. These are scene-specific observations, not a general rejection of prompt scheduling.

Final video review used five overview samples per case and seven consecutive frames around 2.167–2.417s in a [matched comparison](../exports/prompt-bridges-v001/direct/section-013/rife/reviews/preview/v001/contact-sheet.jpg). Both soften or double fine inner geometry near 2.25s. The staged version retains radial ribs while opening its passage; the direct version opens a broader plain arch. The clearer hybrid does not establish a convincing overall smoothness winner. These bounded frame inspections support the comparison but do not replace Olof's playback judgment.

## Verification and cost

Local preflight checked every repaint in the six previous ramp configurations and the earlier dynamic-journey configurations against the previous recipe function: unchanged configurations return exactly the same prompts and sigmas. The new cases have identical noise at all twelve repaint timestamps and identical final text from 2.5s. Only the first four positive descriptions differ.

All **24 new jobs and 410 archive files** are verified locally. Every archived graph retains warped-previous-image initialization, and eight sampled warps were recomputed exactly. See [generation verification](../exports/prompt-bridges-v001/generation-check.json). Inputs, outputs, executed graphs, histories, model verification and runtime receipts are preserved.

Both videos fully decode at **1536×1024, 24 fps, 156 frames, 6.5 seconds**. Each keeps all thirteen source paintings at half-second timestamps and an unchanged native final hold. See [delivery verification](../exports/prompt-bridges-v001/delivery-check.json). The direct control shares the historical opening exactly but differs in decoded RGB from its first new painting onward, with differences accumulating later. The fresh same-runtime direct control is therefore the relevant comparison; this check does not isolate the cause of cross-execution differences.

The retained EU cache supplied all three verified Krea assets with no downloads. ComfyUI remained pinned at `12d5279438bfefc058a269eae805ceab6047777f` (0.34.0). Both cases ran on one RTX 4090; the fresh direct control avoids comparing the treatment against an earlier GPU execution alone. Rendering and automatic archival completed in about 210 seconds after runtime readiness.

After local verification, 48 owned remote input/output files and the experiment scratch directory were removed. The owned Pod was deleted, an empty Pod list confirmed, and the authorized 50 GB model volume retained. Approximately 7m49s at $0.74/hour gives **$0.0964 estimated compute**; with a conservative $0.03 disk allowance, **about $0.13** for this round. Billing was unposted at cleanup. Tracked session spending including the earlier startup allowance is about $1.98 within the original $10 budget; retained-volume ongoing storage is separate.

## Human feedback — 2026-09-13

Olof finds the intermediate prompt descriptions very interesting and notices a few more changes early in the video. He considers this promising, while explicitly saying the value and size of the improvement are not proven. No definitive winner or general improvement is established. He next asks to check whether non-default CFG values have an effect; see the source-verification follow-up in [Krea transition controls](../../../../../docs/research/krea-transition-controls.md).
