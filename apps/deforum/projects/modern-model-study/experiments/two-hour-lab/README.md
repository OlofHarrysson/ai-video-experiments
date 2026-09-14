# Two-hour autonomous learning session

Started 2026-09-14 at 15:43:47 UTC. Start new experiments until approximately 17:43:47 UTC; already-started work may finish afterward. Hard maximum **$10 incremental spend**. Olof delegates experiment choices and wants learning plus a small self-reviewed video shortlist, with concise accounts of promising and unsuccessful approaches.

Keep recurrent previous-image initialization, the existing uv/ComfyUI package and 24 fps output. Preserve every attempt. Record the question and settings before each round; inspect paintings first, then relevant interpolated frames. Distinguish more texture, changed composition and smaller redraws from useful gradual transformation. Change the next round in response to evidence. Finish by verifying local media, cleaning up owned compute/scratch, retaining the authorized model cache and updating the reviewer. No requirement to spend the whole budget.

## Session result

Completed 2026-09-14 17:42:29 UTC, approximately two hours after starting.

The assistant shortlist is [Porcelain Weather — stronger transformation](../../exports/two-hour-lab-v001/r7-porcelain-travel-noise/finish/rife/preview.mp4) (14s) and [Velvet Harbour — short edit](../../exports/two-hour-lab-v001/velvet-harbour-cut/preview.mp4) (11s). These are creative candidates awaiting Olof’s feedback, not selected production defaults. Both retain recurrent previous-image initialization, half-second paintings, three Euler intervals, CFG1, Lanczos motion and 24 fps/RIFE finishing. No interpolated frame feeds back into generation.

[Open the two-film reviewer](http://localhost:3028/). Separate pages keep comparisons manageable: [porcelain revisions](http://localhost:3028/two-hour-porcelain), [velvet revisions](http://localhost:3028/two-hour-velvet), [noise/sampling controls](http://localhost:3028/two-hour-controls), [guidance/text controls](http://localhost:3028/two-hour-conditioning), and [RAW/Turbo diagnostic](http://localhost:3028/two-hour-models). The previous task remains at [transformation stages](http://localhost:3028/transition-stages).

| Round | Question | Finding |
| --- | --- | --- |
| 1 | Can earlier moderate noise open the shell gradually? | It adds detail and small openings, but mostly retains the solid spiral. A shared final peak does not erase the effects of earlier history. |
| 2 | Does the placement of three Euler updates help? | Some shading and aperture changes; no convincing full-transformation improvement. |
| 3 | Can old-subject negative text remove the shell at CFG1.3? | The conditioning changes appearance, but the shell persists. Not an object eraser. |
| 4 | Does continuously blending text embeddings soften the change? | Both verified endpoints reproduce direct prompts. The blend is active, but the main opening still appears in one short interval. |
| 5 | Do two new compositions work with the established recipe? | Ceramic wave → paper landscape → cranes and theatre → mushroom world → harbour both make more interesting films. Major inherited shapes still persist. |
| 6 | Is undistilled Krea RAW a quick remedy? | Native ComfyUI execution works. RAW repaints take about 36s versus 4.9s for Turbo in this screen, and both alter/simplify the unchanged scene. No clear reason to switch. |
| 7 | Can reframing plus stronger transition noise improve the cranes? | More open sky and a larger crane improve the visual progression. Removing the final pullback avoids its reflected edge bands. Higher noise still creates blurred/doubled RIFE intermediates around 8.7–9.3s. |
| 8 | Can direct descriptions turn the inherited curtains into sails? | The revision retains curtains and mushrooms and makes smaller boats. The original’s central sail is clearer; the revision is not featured. |
| 9 | What does noise alone do to one fixed sampling input? | Increasing 0.60→0.74 progressively opens the same spiral into an architectural frame. This is a parameter diagnostic, not a recurrent video or a universal threshold. |

The most useful creative lesson is that material changes were easier than replacing dominant silhouettes in these shots. Changing glaze into paper was visibly progressive; turning a large curved ridge or curtain into a different object remained difficult. Movement can reveal new space and make change more readable. More transition noise can permit a stronger redesign, with a real interpolation cost. Neither more fine detail nor a smooth parameter curve guarantees a smooth semantic transformation.

My next choice would be a short shot whose intended new object follows the existing large shape, with a deliberate move into open space and an early settled ending. Keep the best current recipe while testing one transition at a time. Defer more negative-conditioning and Euler-spacing sweeps, and keep RAW as a documented alternative rather than the next default.

All **307 unique successful image jobs**, graphs, inputs and outputs are local; the final archive verifies **5,117 files** by SHA-256. All selected deliveries have verified frame counts, painting timestamps/pixels and complete decoding. The 11s Velvet edit preserves original frames 0–252 then holds painting 252 for eleven frames; the complete 14s original remains available. No original generation was discarded.

The owned Pod was deleted after local archival; 610 owned remote media files, session scratch and the temporary RAW checkpoint/symlink were removed. The authorized 50 GB model volume is retained. Account balance decreased **$1.3611** during this session; allow approximately **$1.45** including unposted usage, comfortably below $10. Pod billing is still partially posted, so the account debit is not a final itemized invoice. No other paid API was used. Receipts live in ignored `work/two-hour-lab-session/` and the export’s `checks/` directory. The preserved model cache retains its already-authorized ongoing storage cost.

Shared package validation: 54 offline tests. Media review validation: 17 Python tests and two timeline tests. Frozen legacy controls and conditioning endpoints reproduce their expected pixels exactly. Visual review used raw overviews, adjacent transition paintings and targeted RIFE frames; it does not establish every-frame artistic quality.

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

## Round 9: inspect one repaint’s noise response

Freeze the round-one control’s exact warped input, seed and prompt at 3.5s. Run nine independent probes at starting noise 0.60/0.62/0.64/0.64624/0.66/0.68/0.70/0.72/0.74, with the same proportional three-interval Euler recipe and CFG1. Require 0.64624 to reproduce the recorded painting pixel-for-pixel. These are parameter probes from one state, not a time sequence or a substitute for recurrent animation. Unlike the earlier recurrent arms, they separate the immediate noise response from the changing history of previous paintings. Inspect whether small increments change the opening gradually or trigger a major redesign. This is one local response curve, not a universal noise threshold, and changing starting noise also changes the remaining integration trajectory.

## Round 6 findings

All fourteen jobs and 4,219 cumulative archive entries are verified locally. RAW loads natively with the existing encoder/VAE and no additional nodes. Its full opening takes 95.01s, and its median twenty-interval repaint takes 36.23s; Turbo's median three-interval repaint takes 4.88s. The Turbo opening takes 69.14s including the model switch, so that number is not warm eight-step inference time.

Both models change their waves and simplify fine foam without motion or a prompt change. RAW retains strong glossy blue/white shading but makes its foam less irregular; Turbo turns its crest into larger rounded ceramic lobes. Neither demonstrates that repeated repainting converges toward an ever-better version of the original. These six cycles do not establish a universal degradation rate or a model winner. RAW generated a wide inset inside the square canvas; those blank margins also make its lower full-image pixel-change scores unsuitable as evidence of better preservation. The stored diagnostics separate adjacent change and deviation from each model's own opening, with that caveat.

All seven paintings per arm were reviewed, with enlarged fixed RAW wave crops and the first/last paintings. The diagnostic videos hold each actual painting for half a second, with no RIFE. Keep Turbo for this session's moving films; RAW remains a verified alternative for a better matched future screen, not an adopted replacement.

## Round 5 finishing review

Both 14s deliveries are verified at 336 frames and 28 paintings, with the final motion settled. The sampled porcelain transition retains a readable curved form while the surface becomes angular, although its sun briefly deforms. In Velvet, the large mushrooms arrive through a foggy/dissolving intermediate rather than continuous visible growth; interpolation cannot recover a growth path that the paintings did not contain. Inspected Velvet frames 74/77/80 and Porcelain 83/87/91 in addition to the raw painting sequences. Both originals remain available while the revised endings render.

## Revised-ending painting review

Round seven's thirty-three jobs pass remote lineage/graph checks, and every downloaded painting matches that validated receipt before finishing. Removing only the final pullback keeps the original paper-wave composition without its conspicuous late reflected bands. Stronger reframing makes a larger crane emerge from the left-hand folded form. With the same revised motion, the higher-noise arm creates a more distinct, centered crane and opens more sky around it by 9–10s; part of the curved backdrop remains. This is a promising creative result, not a solved smoothness problem: the larger structure still changes markedly between 8.5 and 9s. Reviewed matched paintings at 8/8.5/9/9.5/10/11/13.5s and the settle-only ending. The first interpolation pairs reproduce every frame of the already-inspected original opening pair exactly.

Round eight's ten jobs pass remote verification and the downloaded paintings match their receipts. The revised descriptions add ropes and pale sail-like fabric to the mushroom harbour, but the dominant curtains do not become separate ocean-going sails. It fails its replacement hypothesis. The shorter, gentler ending is less corrugated, yet the original's central boat is more readable. Reviewed matched paintings at 7/8/9/9.5/10/11.5s. Preserve the revision as evidence; the creative shortlist instead uses an eleven-second edit of the original, retaining original delivery frames 0–252 and then holding painting 252 for eleven frames. That keeps the first twenty-two paintings and all intervening RIFE frames, ending before the worst late pullback artifacts. The complete fourteen-second original and every later painting remain archived.

## Final frame review and fixed-input probe

Inspected R7’s two matched RIFE branches at frames 206/209/212/215/220/224/227. The stronger-noise version yields the larger crane and more open centre, but frame 209 has conspicuous soft/doubled surfaces during the large redraw; similar softness remains at 220–224. This is the more expressive candidate, not a demonstrated flicker reduction. The calmer same-motion branch remains selectable.

Round 9’s nine fixed-input probes all pass provenance checks, including exact pixel reproduction of the recorded 0.64624 control. The [contact page](../../exports/two-hour-lab-v001/noise-response/comparison.jpg) shows a mostly solid spiral at 0.60, increasing open ribs by 0.64–0.68 and a more open architectural frame at 0.70–0.74. The holes grow across this sampled parameter range, but the geometry also changes; there is no measured universal linear response. Every probe starts from the identical warped painting and seed. None consumes the prior probe. This separates local noise response from the path-dependent recurrent experiment.

The initial seven-film embedded reviewer exceeded the browser inspection tool’s 64 MiB message limit. The library was split into smaller named pages with the two-film shortlist at the root, preserving all source bytes. Recorded as AF-20260914-193910; large single-file review libraries remain a known tooling limit.
