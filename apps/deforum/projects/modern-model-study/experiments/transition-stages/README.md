# Describing smaller stages of the transformation

Plan recorded before inference, 2026-09-14. Olof says the extra-painting version is a little better, but still holds for a while and then flips in one or two paintings. This round tests descriptions of smaller visible changes and, separately, a lower final noise peak.

All three cases share the previous four/s experiment's paintings through 2s. They retain its exact painting timestamps, seeds, motion, Krea Turbo, CFG1, three Euler intervals and early settling. Each consumes its own warped previous painting. Both working and delivery timelines stay at 24 fps, eight seconds; RIFE 4.25 scale 1 remains outside recurrence. There are 45 fresh paintings: fifteen per case.

| Case | Positive descriptions after 2s | Starting-noise change |
| --- | --- | --- |
| control | Existing shell-with-buildings → hollow pavilion → canyon city | None |
| stages | Narrow seams → small window openings → widening gaps → half-open pavilion → open ribs/street → avenue/arches → city with spiral bridges → identical final city prompt | None |
| stages-capped | Same new descriptions as stages | Cap only the last two transition paintings, 3.75/4s, at 0.66 instead of 0.69336/0.74048 |

The first comparison changes only text. The second keeps that text fixed and lowers the final two noise values. The current noise curve is otherwise preserved, including 0.25 at 4.5s and 0.10 from 5s. Text describes desired visible states rather than issuing next-frame editing instructions. This is not conditioning-embedding interpolation and does not guarantee geometric compliance.

Judge whether meaningful open space develops across several paintings, whether the last reveal remains abrupt, whether the city actually arrives, and whether details remain legible. Inspect every painting and every delivered frame 84–96, expanding the window if an earlier jump appears. A static intact shell is not a success. Mean pixel change is diagnostic only. Default the reviewer to the most informative pair and retain all three choices.

Use one cached short-lived Pod, target below $1 and stop the round before $2. Download and hash-check all generated media and receipts before clearing owned scratch/compute. Keep the authorized model volume. The existing package handles recurrence, schedules, warps, graphs and transport; this directory owns frozen configs and its verification/review script.

From `apps/deforum/`:

```bash
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py prepare
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py render --deployment /ABSOLUTE/DEPLOYMENT.json
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py check
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py pair
# Inspect the first-pair outputs before the full finish.
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py full
uv run --locked python projects/modern-model-study/experiments/transition-stages/run.py delivery
```

Results are preserved under `exports/transition-stages-v001/`.

## Results — 2026-09-14

All three eight-second clips are complete. Finer descriptions change the route toward the city, but do not solve the abrupt structural transformation. Human preference is pending; retain the accepted recipe.

| Case | Observed result |
| --- | --- |
| Current descriptions | Gradual small architectural markings; the main city reveal remains concentrated near 3.75–4s. |
| Smaller described stages | Broader openings and visible streets by 3.5s, with a more open avenue at 4s. The shell is still mostly solid at 3.25s: a large change occurs in the very next painting. |
| Stages + gentler final repaints | More of the spiral/ribs survive at 3.75–4s. The last reveal changes less and the inspected interpolation has less overlapping architecture, but reaches a different, less open composition. It does not address the earlier 3.25–3.5s jump, which precedes the cap. |

The first comparison isolates text: all painting times and actual starting-noise values match. The second isolates the last two noise values, and its paintings through frame 84 are pixel-identical to the uncapped stages. More descriptive states do not ensure correspondingly small image edits. This is one source/seed path and one transformation; it does not establish a universal noise threshold or prove prompt staging unhelpful.

Assistant review covered all twenty paintings per case (shared prefixes checked for identity), every delivered frame 78–96 in the main comparison, and every frame 84–96 in the cap comparison. Contact sheets are preserved under `review/`. RIFE softens the changes, but doubled rings/buildings remain around frame 81/87 and especially 93 in the uncapped version. The final low-noise architecture holds through the ending. These are frame-sequence observations, not a measured flicker score or Olof's playback verdict.

Use the [local reviewer](http://localhost:3028/) for all three choices. It initially compares current descriptions with smaller stages; select **Stages + gentler final repaints** to inspect the cap. The previous timing experiment remains at `/transition-frequency`.

- [Main comparison video](../../exports/transition-stages-v001/comparison.mp4)
- [Current descriptions](../../exports/transition-stages-v001/control/finish/rife/preview.mp4)
- [Smaller described stages](../../exports/transition-stages-v001/stages/finish/rife/preview.mp4)
- [Stages with gentler final repaints](../../exports/transition-stages-v001/stages-capped/finish/rife/preview.mp4)

## Verification and resources

All 45 fresh jobs have verified executed prompts, seeds, sigma schedules, warped-input pixels and parent/output lineage. All twenty control paintings match the preceding four/s experiment pixel-for-pixel. The first interpolation pair was identical across cases and inspected before full finishing. All three deliveries preserve twenty painting anchors across 192 frames at 24 fps, retain the common opening through frame 48, and fully decode. The final eleven frames hold the last painting because the bounded motion has already settled. RIFE never feeds back into generation.

The downloaded archive contains 778 size/SHA-verified files. Archive, generation, prefix and delivery checks are saved locally alongside the experiment. All 51 package tests pass; no new ComfyUI nodes or shared numerical changes were needed. The remote runner used the locked uv package in a separate environment from ComfyUI.

One RTX PRO 4500 Blackwell Pod ran for 15m 11s at $0.72/hour: approximately $0.182 compute, or **$0.21 conservatively including a disk allowance**. Posted billing was still empty at the immediate check; this is an estimate, not a final invoice. After verifying the archive, all ninety owned input/output files and session scratch were removed, and the Pod was deleted. The authorized 50 GB model volume remains; the subsequent Pod listing was empty.

A useful later comparison would give the model more time at a moderate transition noise before the large opening. That remains a hypothesis: it might distribute structural changes, or merely prolong the intact shell. Avoid treating another smoother-looking hold as success at gradual transformation.
