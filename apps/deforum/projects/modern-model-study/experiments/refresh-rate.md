# More frequent, smaller repaints

Status: complete 2026-09-13. All three videos are preserved, verified and available in the local reviewer; human playback preference is pending. Olof approves a frequency/noise comparison and prefers **CFG 1.0**, the official Turbo convention in ComfyUI, over adopting the experimental 1.3 candidate. Keep CFG1 for all three branches.

| Case | Repaints/second | Cadence at 24 fps | Noise ramp | Fresh paintings |
| --- | ---: | ---: | --- | ---: |
| two-current | 2 | 12 | 0.40 → 0.78 → 0.64 | 12 |
| four-current | 4 | 6 | same | 25 |
| four-lower | 4 | 6 | 0.34 → 0.663 → 0.544 | 25 |

Each clip is 6.5 seconds at 24 fps. Preserve the same snail opening, text stages at 1.5/2.5 seconds, three Euler sampling intervals, Lanczos motion stopping at 4s, and RIFE 4.25 scale 1. Noise is now an explicit time curve: linearly interpolate the prior half-second values at inserted quarter-seconds and hold the endpoint values outside that range. The low-noise branch scales the whole curve and all three sigmas by 0.85. This changes both the starting latent mixture and the integration schedule; it is not fewer/more internal sampling intervals.

Common half-second paintings retain the original seeds; inserted quarter-second paintings use a separate reproducible seed range shared by both 4 Hz branches. Inputs necessarily diverge after additional repaints. This controls random seeds at shared timestamps, not identical input images throughout. The 4 Hz cases have one additional late repaint at 6.25s and a 0.25s final hold; the 2 Hz case ends repainting at 6s and holds for 0.5s. Motion is already stationary at both endings.

The comparison is A→B for frequency and B→C for a smaller noise schedule. More calls do not automatically mean smaller changes, quicker semantic progress or smoother video. Review paintings plus selected interpolated windows before asking Olof for taste feedback. All three remain available in the local reviewer; default to the most informative two after review.

[Runner](refresh_rate.py) extends existing helpers with optional cadence, time-based noise and explicit frame seeds. Legacy configs retain their original behavior; local preflight verifies the half-second graph parameters exactly match the prior CFG1 recipe. Plan: 62 fresh jobs on one short-lived cached ComfyUI Pod, archive and hash-check every output before cleanup, retain the model volume. Cap $2 for this round inside the remaining original $10 budget (previous estimated total $2.27).

Pre-render verification: all 15 legacy scene/ramp configurations retain identical recipe values at sampled times; 12 existing timing/interpolation tests pass. The fresh two-per-second control subsequently reproduced all thirteen prior CFG1 paintings pixel-for-pixel (decoded RGB hashes). PNG file hashes differ for new generated frames because file-level metadata is not the same; pixel equivalence is the checked claim.

## Painting findings

The original-noise 4 Hz branch develops a wider central street/canyon view with bridges and copper-roofed buildings by 3.5–6s. The 2 Hz control retains a narrower avenue through the circular structure. The 15% lower-noise 4 Hz branch makes smaller changes but keeps a dominant solid shell/disk with a small central opening through the end; it does not achieve the same open-city conversion. This does not support the initial hypothesis that a blanket 15% reduction would be the best combination for this scene.

Peak mean absolute difference between each painting and its warped input, in normalized RGB, occurs at 3s: 0.0917 for 2 Hz, 0.0894 for 4 Hz at original noise, and 0.0442 for 4 Hz at lower noise. These are change measurements, not smoothness/quality scores. More frequent calls alone did not halve the biggest per-repaint change. Lower noise reduced it, with weaker scene transformation. Additional repaints also introduce more VAE/warp cycles and random-noise samples; this is an end-to-end recurrent-frequency comparison, not an isolated integrator step-size test.

## Execution

One RTX 4090 reused the retained Krea model cache, pinned ComfyUI `12d5279438bfefc058a269eae805ceab6047777f` / 0.34.0, and Torch 2.10.0+cu128. The image pull/start took about three minutes; model hashes and runner imports passed without downloads or dependency installs. The external proxy passed with the repository HTTP client. All 62 histories, executed graphs, CFG1 settings, seed assignments and parent/input/output hashes were verified. Twenty-one sampled warps recomputed exactly on the Mac. The complete 1,018-file archive passed size/SHA256 checks before deletion of the owned 124 remote media files and session directory.

The owned Pod was deleted and absence confirmed; the authorized model volume remains. Elapsed Pod lifetime about 17.8 minutes, compute estimate $0.2196 plus $0.03 disk allowance = **about $0.25**, within the $2 round cap. Billing had no posted record at cleanup. Estimated cumulative original-session spend is about $2.52 of $10. Private archive, verification and cleanup receipts are in ignored `apps/deforum/work/refresh-rate-session/`.

All outputs, comparison sheets, source lineage and diagnostics are under `../exports/refresh-rate-v001/`. The half-second RIFE timing settings (2 source fps, 12× interpolation) and quarter-second settings (4 source fps, 6×) both deliver 24 fps. First-pair previews for all three were inspected before full finishing. Interpolation stays outside the generation loop.

## Delivery and review

All three videos fully decode at 1536×1024, 24 fps, 6.5 seconds / 156 frames. The 13/26/26 source paintings remain pixel-identical at their expected delivery positions before lossy encoding. Final stationary holds are also verified. Receipts: `generation-check.json`, `historical-control-check.json`, `delivery-check.json` and the RIFE manifests under `../exports/refresh-rate-v001/`.

Reviewed matched early/late painting sheets, all three first-pair previews, a finished overview comparing the two 4 Hz branches, and every delivered frame from 2.5–3s for the 2 Hz and original-noise 4 Hz branches. The latter includes an actual intermediate painting at 2.75s where the slower video has an interpolated frame. Both still show some soft/doubled architecture between paintings. The added painting provides a different intermediate structure, not proof of universally smoother or faster semantic change. Assistant favors the original-noise 4 Hz branch as the useful next audition for its wider city; the lower-noise disk is less successful for the intended conversion. Preserve 2 Hz as the accepted default until Olof chooses.

[Open the local reviewer](http://localhost:3028/) and refresh an existing page. Default comparison: 2 paintings/s versus 4 paintings/s at original noise. The lower-noise version is selectable or can be added as a third video. Shared time/frame stepping stays synchronized; painting stepping follows Video 1's anchor timeline. Saved session: `apps/deforum/media_review/sessions/refresh-rate.json`. The prior CFG and prompt-bridge sessions/media remain preserved.

Live reviewer verification: at frame 66 / 2.75s the baseline correctly reports an in-between frame and the 4 Hz video reports painting 11. All three loaded, played with shared controls, and reached frame 155 together with final painting indices 12/25/25. The dedicated browser layout keeps the comparison frames visible.
