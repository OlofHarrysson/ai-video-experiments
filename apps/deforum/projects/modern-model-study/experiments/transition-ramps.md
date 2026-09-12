# Shaping a recurrent scene transition

Status: completed 2026-09-13 (Europe/Stockholm). All six videos are local and verified; Olof's playback preference is pending. Olof likes the 24-second changing-world film and requests lower starting noise, different peaks, more diffusion paintings and different rise/return curves. CFG and other transition controls are researched separately in [Krea transition controls](../../../../../docs/research/krea-transition-controls.md).

**Lower starting noise mostly delays the conversion. A higher peak opens the shell into a much wider city vista, but also creates a larger change between adjacent paintings.** Longer rises offer more intermediate structure; smooth rise/return curves alone do not clearly solve abrupt semantic changes. Keep the liked film's recipe as the default pending human review. These are useful controls over persistence and replacement, without an established new quality winner.

Six matched 6.5-second probes start from the same saved snail painting and use the same city prompt, seeds, first bounded spatial phrase, three Euler intervals, CFG 1, half-second repaints and RIFE 4.25 scale 1. Each has twelve new paintings. The first four seconds retain the opening motion phrase; motion then holds, making later rebuilding easier to inspect. These are fresh controls, not reuses of the old multi-phrase film.

| Case | Change from comparison | Rise | Return |
| --- | --- | --- | --- |
| control | Accepted noise schedule | 0.60/0.64/0.68/0.70 | Immediately to 0.64 |
| lower | Lower starting value, same normalized four-painting rise | 0.40 → 0.70, four paintings | Immediately to 0.64 |
| longer | Stretch lower's piecewise rise across six paintings | 0.40 → 0.70, six paintings | Immediately to 0.64 |
| eased | Change longer's rise shape to smoothstep | 0.40 → 0.70, six paintings | Immediately to 0.64 |
| soft-return | Add a three-painting smooth return after eased | 0.40 → 0.70, six paintings | Three paintings to 0.64 |
| higher-peak | Raise soft-return's peak, same timing and shapes | 0.40 → 0.78, six paintings | Three paintings to 0.64 |

The controlled knob is the entire proportional sigma schedule, not an independent noise addition: `[0.6, 0.512844085693, 0.310901075602, 0] * starting_sigma / 0.6`. Every repaint starts from the warped previous painting. Counts here refer to separate recurrent paintings, not sampling intervals inside one painting. More paintings in the ramp change the transition timing, while total duration and total repaint count stay matched.

The [runner](transition_ramps.py) generates immutable [configurations](transition-ramp-configs/control.json), reuses the existing recurrent runner and local finisher, and preserves all jobs under `exports/transition-ramps-v001/`. The [curve plot](../exports/transition-ramps-v001/ramps.png) shows each painting's starting noise against actual time. All cases settle at 0.64; independently varying that final level remains untested. A higher peak also raises intermediate ramp values, rather than changing only one painting.

## Results and all videos

Each linked clip is 6.5 seconds at 24 fps with the same RIFE finishing. The useful shortlist is **soft-return versus higher-peak**: identical start, rise/return shapes and painting counts, with only peak amplitude changed.

| Video | Observed result | Interpretation |
| --- | --- | --- |
| [Original ramp](../exports/transition-ramps-v001/control/section-013/rife/preview.mp4) | Buildings appear at 0.5s; the shell opens into a broad arched city passage at 1.5–2s. | Earlier environment change; remains a useful control. |
| [Lower start](../exports/transition-ramps-v001/lower/section-013/rife/preview.mp4) | Intact snail through 1s, followed by a large cavity change at 1.5–2s. The later city retains a strong spiral. | More time with the old subject, without clearly spreading its largest replacement. |
| [Longer rise](../exports/transition-ramps-v001/longer/section-013/rife/preview.mp4) | A small architectural aperture at 2s grows into arches at 2.5s and a passage at 3s. | More staged opening, accompanied by a longer initial dwell. |
| [Smooth rise](../exports/transition-ramps-v001/eased/section-013/rife/preview.mp4) | Similar shell-to-passage progression at 2–3s. | Changing the rise curve alone shows no clear semantic-smoothing advantage. |
| [Smooth rise and return, peak 0.70](../exports/transition-ramps-v001/soft-return/section-013/rife/preview.mp4) | The spiral becomes a nested tunnel of arches, buildings and towers. | Strong continuity of the original motif; the gentler return does not visibly transform the result. |
| [Same curve, peak 0.78](../exports/transition-ramps-v001/higher-peak/section-013/rife/preview.mp4) | The shell opens into a wide canyon avenue at 2–2.5s, followed by bridges and towers with clear depth. | Best example of escaping the inherited shell, at the cost of a larger painting change. |

All use one city description from the first new repaint onward. Low starting values therefore preserve the snail despite the changed text. Later outcomes carry the accumulated recurrent history; this is one scene and seed sequence, not six independent final-image samples. Later surfaces become more illustrative in several cases, so extra dwell does not establish better material preservation.

## Review evidence

Main review inspected the painting sheets across all six cases, with shared prefixes verified in decoded RGB. The [independent control/lower review](transition-ramps-independent-review.md) agrees that lowering the start mainly delays the conversion and keeps a stronger spiral motif. Its scope is paintings, not playback quality.

Local video review includes first-pair intermediate frames and evenly spaced overview samples plus a dense 2.167–2.458s window for the shortlisted clips: [peak 0.70 review](../exports/transition-ramps-v001/soft-return/section-013/rife/reviews/preview/v001/contact-sheet.jpg), [peak 0.78 review](../exports/transition-ramps-v001/higher-peak/section-013/rife/reviews/preview/v001/contact-sheet.jpg). In that window, 0.70 develops radial architectural detail while retaining the center. At 0.78, a much wider opening emerges; intermediate frames around 2.25s show softened/doubled arch and shell detail. RIFE spreads this replacement over time but cannot supply missing diffusion-generated stages. These bounded frame inspections do not establish a human playback preference or exclude artifacts elsewhere.

The four longer-rise cases share the lower-start case's first interpolated pair exactly in decoded RGB; eased and soft-return share paintings through 3s. Their repeated frames need not be treated as independent visual evidence.

## CFG and next experiment

CFG amplifies the prompt-conditioned prediction relative to a negative/unconditional prediction. It does not directly specify how much of the previous image to retain. Official Krea Turbo uses no extra CFG: the Krea CLI expresses that as 0, while ComfyUI expresses it as 1. Text remains active. Our negative branch is zeroed, so reducing CFG below 1 would blend toward that prediction rather than protect the previous image. We have not established that other CFG values cannot work; they are outside the author's recommended Turbo recipe and were not varied here.

The [source-backed research](../../../../../docs/research/krea-transition-controls.md) separates CFG, initial latent/noise mixing, internal sigma placement, descriptive bridge prompts, conditioning blends and correlated noise. Current starting-noise changes also rescale the internal sampling trajectory. A smooth scalar ramp does not guarantee a smooth change in objects or scene layout.

The next recommendation is a matched test of a few fixed intermediate descriptions, such as shell with buildings → hollow architectural shell → city passage, against the unchanged city prompt. Use one chosen noise curve and preserve the model, motion, repaint interval and RIFE. This is a hypothesis for supplying meaningful intermediate forms, not a rendered result. CFG and more complicated noise controls remain later candidates.

## Execution and verification

The temporary A100 used the pinned ComfyUI image and runtime commit `12d5279438bfefc058a269eae805ceab6047777f`; existing Krea FP8, Qwen3VL and VAE asset checks passed. All **72 new jobs and 1,192 archive files** are verified locally. Twenty-four recomputed warp inputs match the archived remote initialization exactly. See [generation verification](../exports/transition-ramps-v001/generation-check.json).

All six videos fully decode: **156 frames, 1536×1024, 24 fps, 6.5 seconds** each. Each retains its shared opening and twelve new paintings at the original half-second timestamps. The final half-second holds the last native painting because bounded motion has settled. See [delivery verification](../exports/transition-ramps-v001/delivery-check.json). RIFE stays outside the feedback loop.

The owned Pod was deleted after approximately 22 minutes, and an empty Pod list was confirmed. The authorized EU model volume remains. Estimated compute is **$0.5826**, plus a conservative **$0.03 disk allowance**, about **$0.61**; this Pod's billing was unposted at cleanup. Previous successful sessions posted $0.1743 and $0.8445. Including a $0.25 allowance for the earlier startup failure, the tracked session total is approximately $1.88 within the original $10 budget; retained-volume ongoing storage is separate.

The long SSH output stream stopped updating even though inference had completed. A fresh connection confirmed an empty queue and all 72 completed jobs before archival; no jobs were resubmitted. This delayed cleanup briefly and was logged centrally as AF-20260913-002252.

The fresh control reproduces the earlier journey through 3.5s exactly in decoded RGB pixels (eight paintings including the shared opening). Whole PNG file hashes differ because embedded workflow metadata changes with the experiment case. Comparisons use decoded pixels for reproduction and whole-file hashes for transfer integrity. The momentary incorrect runtime diagnosis was corrected and recorded centrally as AF-20260913-001020.
