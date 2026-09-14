# Extra paintings during the morph

Plan recorded 2026-09-14 before inference. Olof selects option one: compare two versus four diffusion paintings per second during transformation, keeping the holding policy identical. This follows [early settling](../early-settle.md), with a known remaining large shell-to-city change.

Both eight-second clips share the accepted paintings through 1.5s, the exact staged descriptions and time-based noise curve from early-settle, Krea Turbo, CFG1, three Euler sampling intervals, bounded Lanczos motion, 24 fps and RIFE 4.25 scale 1. Two paintings/s remains the opening and ending schedule in both. The treatment adds paintings at 2.25, 2.75, 3.25 and 3.75 seconds; it therefore has four/s between the paintings at 2s and 4s. The noise curve reaches 0.74048 at 4s, drops to 0.25 at 4.5s and 0.10 from 5s. Text changes stay at 2/3/4s. No extra CFG, noise reduction or new prompts are combined with this test.

Common timestamps keep their original seeds. Added paintings get a separate deterministic seed sequence. After the first inserted repaint, each branch consumes its own previous painting; its ending has the same settings, not identical image content. The continuous spatial path has identical total displacement; extra repaints also introduce extra resampling/VAE cycles. This tests recurrent repaint frequency, not a pure numerical step-size change.

The control has 16 total paintings, the treatment 20; 12+16=28 fresh jobs. Both deliver 192 frames, retaining each painting at its exact timestamp. Interpolation stays outside recurrence. Motion has settled by the last painting at 7.5s; the final eleven frames hold it. Use one cached short-lived Pod, target below $1 and stop the round before $2; archive all inputs/outputs/receipts and remove owned compute/scratch, retaining the authorized model volume.

Review every painting and dense matched frames around 3.5–4s. Ask whether the extra paintings create useful intermediate structure, or merely add more redesign. Judge the scene arrival, sharpness, larger redraws and RIFE doubling separately. Less pixel change alone is not a smoothness score. Show the pair in the local reviewer and chat.

Commands from `apps/deforum/`, after `uv sync --locked`:

```bash
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py prepare
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py render --deployment /ABSOLUTE/DEPLOYMENT.json
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py check
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py pair
# Inspect both pair previews before continuing.
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py full
uv run --locked python projects/modern-model-study/experiments/transition-frequency/run.py delivery
```

All outputs are preserved under `exports/transition-frequency-v001/`. Configurations are frozen alongside this note and copied into each export. The app package owns recurrence; this directory owns experiment selection, comparison and checks.


## Result and review — 2026-09-14

Both [two paintings/s](../../exports/transition-frequency-v001/two/finish/rife/preview.mp4) and [four/s during the morph](../../exports/transition-frequency-v001/four-transition/finish/rife/preview.mp4) are complete. The [side-by-side video](../../exports/transition-frequency-v001/comparison.mp4) and [local reviewer](http://localhost:3028/) show the matched pair. The preceding early-settle comparison remains at `/early-settle`. The dedicated browser comparison is verified with both frames visible, correct irregular painting labels and playback through the final hold.

The assistant tentatively favors the extra-painting version for its developing architecture, not as a proven smoothness fix. At 2.5–3.5s it introduces more windows and holes in the shell; the extra painting at 3.75s exposes a more legible passage. At 4s it reveals an open ribbed ring, turquoise roofs and a broader city composition. The control keeps a more solid shell until its larger opening change. Both retain their different final architecture during low-noise settling. Human playback preference remains pending; no global baseline change.

The larger reveal remains. Reviewing every delivered frame 84–96 shows doubled/translucent structures around the control's 89–92 and treatment's 93–94. Extra paintings provide useful stages, but their last interval still crosses a substantial reconstruction. Mean absolute RGB change from the actual warped input at frame 96 is 0.080 for the control and 0.087 for the treatment. This measurement does not establish flicker or quality; it also does not support a claim that the final repaint became smaller. Extra painting events do not automatically mean smaller edits at the same noise.

Review scope: all sixteen/twenty painting slots, including the four inserted paintings; the first-pair RIFE midpoint in both cases; every delivered frame 84–96 at matched timestamps; sampled full scenes and final settling. Contact sheets are under `review/`. The eight-second comparison fully decodes. Review remains selective outside that dense transition window and cannot replace Olof's playback/taste judgment.

## Execution and verification

- All 28 new jobs, requested/executed graphs, prompt IDs, embedded PNG provenance, actual warped pixels, parent/output hashes and collection records pass `run.py check`. The first new painting at 2s is pixel-identical across branches; differing PNG graph metadata means its file bytes differ. Delivered pixels through frame 48 match exactly.
- Both 1536×1024 deliveries have 192 frames at 24 fps, preserve every painting at its intended timestamp and end with eleven hold frames after painting 180. All delivery frame hashes and interpolation fractions are verified. RIFE 4.25 scale 1 uses each actual 6- or 12-frame interval; no interpolated image feeds recurrence. First-pair checks precede complete finishing.
- This is a fresh matched control on one RTX PRO 4500 Blackwell, not a claim to reproduce the older A100 run. Only the four copied opening paintings match the historical file hashes. Both new branches use the same verified model files, ComfyUI 0.34.0 and Torch 2.10.0+cu128 runtime.
- The uv runner was installed separately with `uv sync --locked --no-dev`, preflighted and used for remote recurrence. ComfyUI's Torch environment was unchanged. The public endpoint completed the first job; the remaining loop ran on the Pod to avoid repeated image transfers. RIFE finishing ran locally on MPS.
- All 490 remote archive files pass local size/SHA checks. The archive also contains the original generation runner source. Fifty-six owned ComfyUI media files and the owned session scratch were removed after verification, then the Pod was deleted. The authorized 50 GB `deforum-models` volume remains.
- Pod lifetime was about 14m16s at $0.72/hour: compute estimate $0.1712, conservative total estimate **$0.19** including a disk allowance. The billing read had no posted records yet; that is not a zero-cost claim. No new inference was used for RIFE or review.
- Local suite: 51 tests pass. Irregular painting times, parent selection/resume and uniform interpolation-plan equivalence are covered. Historical early-settle generation checks and recorded response replay pass. Ruff passes for changed numerical code and the new experiment. Infrastructure readiness/log inconsistency is recorded centrally as AF-20260914-141001.

Private operational evidence is in `work/transition-frequency-session/`, including archive inventory, verification, cleanup/cost receipt, model/import preflights and logs. Public experiment evidence and videos remain under `exports/transition-frequency-v001/` locally; large media is gitignored.

If this trajectory is preferred, a useful follow-up would keep these painting times and adjust only the final two repaint noise values or their prompt descriptions, aiming to distribute the 3.75–4s opening change. That is a hypothesis, not an additional experiment run here.

## Human feedback

Olof finds this a little better, but says the fundamental problem remains: little changes for a while, then the image flips in one or two repaints. Extra repaint frequency has not solved gradual transformation. He suggests intermediate descriptions may help and authorizes continued experiments.
