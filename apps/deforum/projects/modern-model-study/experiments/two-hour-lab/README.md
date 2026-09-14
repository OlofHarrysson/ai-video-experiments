# Two-hour autonomous learning session

Started 2026-09-14 at 15:43:47 UTC. Start new experiments until approximately 17:43:47 UTC; already-started work may finish afterward. Hard maximum **$10 incremental spend**. Olof delegates experiment choices and wants learning plus a small self-reviewed video shortlist, with concise accounts of promising and unsuccessful approaches.

Keep recurrent previous-image initialization, the existing uv/ComfyUI package and 24 fps output. Preserve every attempt. Record the question and settings before each round; inspect paintings first, then relevant interpolated frames. Distinguish more texture, changed composition and smaller redraws from useful gradual transformation. Change the next round in response to evidence. Finish by verifying local media, cleaning up owned compute/scratch, retaining the authorized model cache and updating the reviewer. No requirement to spend the whole budget.

## Round 1: earlier moderate noise

The last test's finer descriptions still keep a mostly solid shell until 3.25s, then open it sharply at 3.5s. Test whether earlier time at moderate noise can introduce meaningful open space over several repaints.

All four cases reuse the same paintings through 2s, identical fine prompt stages, seeds, movement, painting timestamps, CFG1 and three Euler intervals. Each is eight seconds with twenty paintings, fifteen newly rendered. The control uses the prior capped curve. Alternatives use 0.55 or 0.60 from 2.25–4s; a fourth holds 0.55 through 3.5s before rising to 0.60/0.66 at 3.75/4s. All settle to 0.25 at 4.5s and 0.10 at 5s.

Inspect whether windows become openings and streets across several paintings, or whether these settings merely delay the reveal, flatten the shell, or introduce unrelated detail. The previous twenty control paintings provide an exact reproducibility check. Later rounds remain undecided.

## Round 2: where the three Euler steps happen

Hold the earlier 0.60 plateau, text, seeds, motion and painting times fixed. Compare the round-1 proportional three-interval control with three other placements. At transition noise 0.60, these are 0.60→0.40→0.20→0, 0.60→0.30→0.10→0, and 0.60→0.55→0.50→0. Each still has three model evaluations per repaint and the same initial image/noise mixture. The unchanged low-noise holds scale the same ratios. Fifteen new paintings per case.

The [official Krea sampler](https://github.com/krea-ai/krea-2/blob/main/sampling.py) uses Euler updates whose size depends on the difference between successive sampling times; Turbo was trained with a fixed shifted schedule. These custom partial schedules are experiments, not official recommendations. Test whether changing that allocation affects crispness, redraw size or semantic conversion. The shared package accepts explicit `sigma_ratios`, rejects nondecreasing/nonfinite schedules, and retains the old numerical expression when this option is absent. Tests verify the actual graph, unchanged initialization and parent recurrence.

## Round 1 findings

All twenty fresh control paintings reproduce the previous pixels exactly. The three earlier-noise alternatives add small buildings sooner but retain a large solid spiral. The 0.60 plateau shows a gradually opening central hole and clear detail, yet fails to produce the control’s broad open city. The early 0.55 plus 0.66 peak also stays closed: ending noise alone does not determine the result; the inherited path matters. This is one source and seed path, not a universal threshold. All 60 new jobs and 1,026 archive entries are verified locally.

## Round 3: negative conditioning at modest guidance

Keep round-one’s 0.60 plateau and original Euler placement. Compare zeroed, encoded-empty and `A closed intact spiral snail shell.` negative conditioning at fixed CFG1.3 during 2.25–4s. Reuse the CFG1 plateau as context; the causal negative comparison is among the three CFG1.3 arms. Switch all three to CFG1 at 4.5s for the same low-noise hold. Each consumes its own previous painting and has fifteen new repaints.

The [source review](research-prompt-control.md) confirms these inputs differ and that external CFG is active; Turbo nevertheless recommends guidance disabled. The narrow question is whether an explicit old-subject negative opens the solid shell gradually at the same noise. Watch for increased redraws or contrast instead. An optional graph transform keeps these experimental controls in the session runner; tests retain parent recurrence and reject changed graphs on resume. No new custom nodes or model weights are required.

## Round 2 findings

Different Euler spacing changes the position of windows and the width of the central opening. Earlier larger updates yield a slightly larger aperture and strong metal shading; the large final update gives simpler panels. None removes the dominant solid shell or establishes a smoother full conversion. Retain the original spacing. All 45 jobs and 1,775 cumulative archive entries are verified locally. Three representative transition paintings and final paintings per arm were inspected, alongside the 0.60 control.

## Round 4: continuous text conditioning

Compare a hard prompt switch at 3s with a linear blend from the old text embedding to the new embedding over 2–4s. Both use the same new concise prompt pair, the original capped noise ramp, CFG1, three original Euler intervals and identical recurrent input, seeds and motion. This tests embedding blending against switching; comparison with earlier elaborate descriptions would also change wording.

The active Krea tokenizer returns one 97-token batch for both complete inputs, with common suffix positions aligned. The intended conditioning shape follows the inspected Krea adapter; no hidden-state tensor was exported. Before recurrent inference, test each blend endpoint against its direct prompt on the exact same image/noise, plus a CFG1 encoded-empty-negative check. Require pixel-identical outputs. This empirical gate supplements the tokenizer/source check; a failed endpoint stops the experiment. No padding machinery or custom model node is added.
