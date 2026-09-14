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

## Round 5: two complete changing-world shots

Generate and screen fresh same-model openings for the [Velvet Flood and Porcelain Weather concepts](creative-plan.md). Each fourteen-second shot has twenty-eight paintings at half-second intervals, three distinct environments and two staged transitions. Use the established three-interval Euler recipe and CFG1. Each transition rises 0.40→0.54→0.60→0.64→0.68→0.70, returns through 0.64/0.40 and settles at 0.15. This is a creative application, not a causal two-arm comparison.

The main agent increases the proposed motion amplitudes moderately to make spatial movement readable; each phrase still eases and stops, with a wider final view. Convert horizontal normalized-width coordinates to the package’s normalized-height units using 1536/1024. Keep the final half-second motion settled. Screen openings before feedback and inspect the raw scene transitions before RIFE. These new compositions test whether our current recipe works beyond the dominant spiral shape.

## Operational checkpoint

At approximately 16:25 UTC, the account balance had fallen by about $0.49 from the session-start snapshot; current account spend rate was $0.746/hour, including the owned GPU and storage. This remains well below the $10 cap. The working Pod and cached model/runtime are unchanged. The shared package's 54 offline tests pass.

The local redirected SSH progress stream became stale while remote inference and archival continued. Direct remote receipts corrected an initially premature collection-stall diagnosis; subsequent rounds write their progress log on the Pod. Recorded centrally as AF-20260914-182316. No job was resubmitted or model/runtime changed in response.

## Round 3 findings and opening review

All 45 jobs and 2,522 cumulative archive entries are verified locally. Zeroed conditioning at CFG1.3 adds considerably more fine structure and background buildings than CFG1. Encoded-empty and subject-negative branches produce cleaner broad surfaces, but neither opens the central shell into a full city. The old-subject negative is not an object-removal switch: the shell remains especially solid in its arm. The low-noise CFG1 ending retains each branch's established design. Keep these as examples of guidance direction changing appearance, not a smoothness solution.

Reviewed raw frames 54/66/78/84/90/96/108/132/180 for these comparisons. The new creative openings both pass: Velvet Flood has readable side curtains, reflected water and an intentionally open middle; Porcelain Weather has a strongly sculpted white/cobalt wave and ample pale sky. Continue both unchanged into their planned feedback shots. The prompt blend's old/new endpoints and CFG1 empty-negative check all reproduce the corresponding direct painting pixel-for-pixel in the active runtime; the thirty-painting recurrent blend/switch comparison is now running.

## Round 6: undistilled Krea RAW diagnostic

The research note initially recommended deferring because storage, transfer speed and execution time were unknown. A fresh check found about 150 GB free on the Pod’s temporary disk, and a five-minute-bounded download completed with the exact published SHA-256 at 16:34:28 UTC. RAW is stored only in owned temporary disk, with one owned model-directory symlink; both will be removed. No runtime/node installation or retained-volume resize was needed.

Test the porcelain-wave prompt at 1024² with each model generating its own opening. This preserves same-model initialization throughout each arm, rather than feeding a Turbo painting into RAW. Keep the prompt unchanged, motion disabled and six paired repaint seeds. RAW uses its official full 52-interval float32 grid at mu0.90625 and Comfy CFG4.5 with encoded-empty conditioning; Turbo uses eight full intervals at mu1.15 and CFG1. For repaints both start at noise0.60, but RAW takes twenty intervals following its full grid’s tail, while Turbo keeps our established three intervals. Time one RAW opening and repaint before committing to the remainder; cap this diagnostic at fourteen jobs and about twenty minutes of inference.

Compare each arm’s retained geometry/detail against its own opening and distinguish adjacent redraw from accumulated drift. Different openings, checkpoint training, guidance and integration cost make this a model-recipe screen, not proof about distillation alone. Keep RAW outputs separate from the ongoing Turbo creative films.

## Round 4 findings

The five fixed-input endpoint checks pass, and all thirty recurrent jobs are verified locally in the 3,123-entry cumulative archive. Blending the two text embeddings changes which buildings emerge and the geometry inside the central aperture, but the dominant shell remains in both arms. The main central opening still appears between 3.5 and 3.75 seconds in both. This establishes that the blend is active and reproducible, not that it solves abrupt semantic change. Reviewed every selected comparison at 2.25/2.75/3.25/3.5/3.75/4/4.5/5.5/7.5 seconds. Keep deliberate descriptive stages as the creative default; preserve embedding blending as an available experimental control.

## Round 5 first painting review

Porcelain Weather visibly changes its glaze/foam into folded material and terraced land over 3–5s. Small origami cranes appear by 8–9s; the dominant wave persists as a curved paper ridge. The intended full replacement with a large airborne crane does not happen. Late zoom-out introduces conspicuous reflected edge patterns during the low-noise hold. This is a motion-boundary issue distinct from repaint redesign. Reviewed raw paintings at 0/2/3/4/5/6/7/8/9/10/12/13.5s; adjacent transition inspection and finishing remain pending.

## Round 7: improve the porcelain ending

Three bounded branches use the exact existing opening and retain every earlier painting. First, remove only the final zoom-out phrase after 10.2s, restarting from the existing 10s painting; seven new repaints isolate that motion-boundary problem. Second, restart at 7s, replace the 7.3–10.5s phrase with a stronger push toward the right-hand open sky, and omit the final pullback; thirteen new repaints test whether reframing can make the composition develop beyond the inherited wave. Third, keep that exact revised motion but raise only the second transition’s noise to 0.70/0.78/0.82/0.72 at 8.5/9/9.5/10s. It tests whether a stronger transition can replace the large form, while explicitly checking the expected risk of a larger redraw. All three retain text, CFG1, original three-interval Euler placement, painting times, seeds and 24 fps/RIFE. No mask or outpainting node is added.

## Round 8: curtains become sails

The independent [Velvet painting review](velvet-review.md) identifies a coherent mushroom harbour, but large curtains/mushrooms persist while new boats appear in the middle. Accept its single ten-repaint branch from the existing 6.5s painting: explicitly describe those dominant red side forms as partly furled triangular sails, then as sails mounted on hulls, ending in open ocean. Keep the existing rise to 0.70, return earlier at 10s, shorten the turning phrase and replace the final pullback with a small translation. Finish at twelve seconds with settled motion. This deliberately combines creative changes; it tests a practical revision rather than isolating one parameter. Inspect whether an existing side form becomes a sail, rather than merely adding a small new boat. The package's scale component is global; its twist is localized by radius, so “local zoom-out” in the independent note is an imprecise description of the composed motion.
