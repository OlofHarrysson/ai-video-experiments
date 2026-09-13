# Does extra CFG help recurrent Krea transitions?

Status: complete 2026-09-13. All four videos are verified locally and available in the media reviewer; human playback preference is pending. Compare ComfyUI CFG **0.8, 1.0, 1.3 and 1.6** with the existing staged shell → hollow pavilion → canyon-city prompts. Olof finds those stages promising but unproven and approves this bounded CFG test.

Reuse the exact same saved Krea opening, prompt schedule, incrementing seeds, 0.40→0.78→0.64 starting-noise curve, three Euler intervals, bounded Lanczos motion, 0.5-second repaints, 24 fps and RIFE 4.25 scale 1. Four 6.5-second clips each contain 13 paintings (12 fresh). Render a fresh CFG1 control in the same runtime. Only CFG changes; retain `ConditioningZeroOut` as the negative conditioning. This is not an encoded-empty-negative comparison or an official Krea CLI reproduction.

Review the actual paintings before RIFE finishing: detail, scene recognition, change between paintings, color/contrast drift and broken geometry. Off-1 predictions incur additional model work. Higher CFG could help recognition or amplify redraws/artifacts; lower CFG could weaken prompt response. These are hypotheses, not promised outcomes. No CFG winner is selected in advance.

The runner is [cfg_audition.py](cfg_audition.py), with immutable JSON recipes under `cfg-audition-configs/`. It uses the existing recurrent runner, which now accepts an optional CFG value while preserving 1 for earlier recipes. Execution receipts must verify all parent/input/output hashes, executed CFG, positive and negative connections, and matched settings. Preserve every output and put the strongest comparison in the local media reviewer, with all four selectable. Session cap $2 within the previously authorized $10 session; retain the model volume and delete the owned Pod after local archive verification.

## Painting findings

CFG is visibly active in this workflow. At 2s, 1.3/1.6 already develop fine architectural ribs and surface texture; 0.8/1.0 retain a simpler shell. At 2.5s the higher-guidance variants open a larger passage into the city. By 4–6s, 1.6 has the densest stairs, balconies and rock texture, while 1.0 retains broader, smoother surfaces. The lower value 0.8 adds no clear advantage in this sample.

More detail does not establish smoother animation. The largest measured repaint change is at 3s in all four cases: mean absolute RGB difference from each warped input is 0.090 / 0.092 / 0.112 / 0.139 for CFG 0.8 / 1.0 / 1.3 / 1.6 respectively (normalized to 0–1). This locates a transition worth inspecting; it is not a perceptual quality score. Each later input inherits its own branch, so these are recurrent trajectories rather than isolated identical-input comparisons.

Assistant shortlist: CFG 1.0 against 1.3. The latter offers more architectural development without the strongest texture amplification. Keep 1.6 available as a more detailed alternative. Olof has not selected a CFG winner; retain the existing default of 1.0 until playback feedback.

## Execution and preservation

One short-lived RTX 4090 used the retained EU model cache, pinned ComfyUI `12d5279438bfefc058a269eae805ceab6047777f`, Torch `2.10.0+cu128`, and the cu128 cached virtual environment. No model download was required. Forty-eight fresh jobs completed; 799 archive files were downloaded and SHA-256 verified before remote cleanup. All executed graphs match their submitted graphs and expected CFG/positive/zeroed-negative connections. Parent, initialization and output hashes verify recurrence; 16 sampled warps recomputed exactly on the Mac.

The owned Pod and its temporary session/input/output files are deleted; the authorized model volume remains. Approximate Pod lifetime: 20.6 minutes, about $0.254 compute plus $0.03 disk allowance = **$0.28 estimated**. Billing had no posted record at cleanup. This remains below this round's $2 cap and brings the original $10 session's estimated total to about $2.27. Setup, transfer and verification time are included; this is not an inference-only price.

Local evidence is under `../exports/cfg-audition-v001/`: `generation-check.json`, `repaint-change.json`, `paintings-matched-early.jpg`, `paintings-matched-late.jpg`, and each case's preserved anchors, warped inputs and job graphs. Exact remote archive and cleanup receipts remain in ignored `apps/deforum/work/cfg-audition-session/`. The four first-pair RIFE previews were visually checked before full finishing.

Measured warm execution medians: CFG 0.8 = 8.018s; 1.0 = 4.558s; 1.3 = 8.093s; 1.6 = 8.082s. The first 0.8 painting took 85.017s including model initialization. These are ComfyUI job timings, excluding archive transfer and local RIFE. Off-1 guidance evaluated both branches and took about 1.8× the warm baseline time on this runtime.

## Finished video review

All four deliveries fully decode: 1536×1024, 24 fps, 6.5 seconds, 156 frames. All thirteen painting frames are pixel-identical in the pre-encode delivery sequence; the final eleven frames retain the stationary final painting. `delivery-check.json` records video hashes and validation. RIFE 4.25/scale 1 is unchanged and never feeds generation.

Reviewed matched painting sheets, all four first-pair previews, the baseline overview, an overview comparing 0.8 with 1.6, and every displayed frame from 2.5–3s for 1.0 versus 1.3. Both shortlisted videos retain soft/doubled edges around the midpoint of that transition. The 1.3 branch develops architecture earlier and ends with more texture, but these samples do not establish smoother playback. No black or broken delivery frames appeared in the inspected samples; this is bounded visual review, not an assertion that every artifact is absent.

Open [the local reviewer](http://localhost:3028/) and refresh an already-open page. It defaults to CFG 1.0 versus 1.3; all four variants are selectable. Painting stepping, matched displayed frame 66 at 2.75s and frame 72 at 3s, and generation-detail text were verified in the live browser. The earlier prompt-bridge session and media remain preserved. The saved session is `apps/deforum/media_review/sessions/cfg-audition.json`.

The useful conclusion is that off-1 CFG is executable and visibly consequential in our Krea feedback loop. It can be auditioned as a detail/transformation control. It is not a direct previous-image retention slider and did not resolve the observed interpolation artifacts. Keep 1.0 as the default pending Olof's taste feedback; 1.3 is the assistant's meaningful alternative.
