# Three-step morphing: interpolation and cadence

## Experiment recorded before execution

Olof prefers the detail of the three-step Krea continuation and wants gradual morphing. He suspects abrupt diffusion redraws are the main problem. This round contains two bounded controls before changing diffusion noise or sampling strength.

1. Reuse the accepted cadence-3 anchors from `turbo-transitions-v001/tail-3`. RIFE 4.25 estimates five intermediate frames per anchor pair, delivering 24 fps. It spans the entire repaint interval, changing display assembly only. Preserve the original warp-only final quarter-second, where no next generated anchor exists. This may smooth transitions but cannot repair the generated anchors themselves and may alter the prescribed motion between them.
2. Generate the same three-second continuation at cadence 2 instead of 3: the same opening, timed twist/expansion, model, prompt, Euler/simple schedule and last three native Turbo intervals. This increases repaints from 11 to 17. Seeds increment once per repaint starting at the same first repaint seed; extra repaints necessarily change which seed falls at a given time. No RIFE in this branch.

Both retain recurrent initialization from the warped previous generated image. No explicit image blending, regional protection, extra noise, depth or new reference conditioning. Cadence changes recurrence count and movement per repaint, so it is not an isolated interpolation experiment. Preserve all outputs and inspect repaint boundaries before human review.

## Interpolation result

Complete locally using the existing pinned RIFE 4.25 MPS runner. Eleven pairs took approximately 14.3 seconds of network inference, excluding initialization and encoding. All 12 generated anchors remain pixel-identical at their original timestamps. There are 55 inferred frames, 12 generated anchors, and five original warp/duplicate frames in the final quarter-second; 72 delivery frames at 24 fps, exactly three seconds. Raw RIFE output with its default final holds is preserved separately; the delivered assembly replaces that final interval with the original motion.

The first pair, five overview samples, and every delivered frame around selected repaint boundaries were inspected. RIFE connects changing arches and patterns gradually, but thin ornaments can bend or compress as it matches different structures. It preserves the same generated detail and overall evolution; it does not correct the diffusion changes. These are sampled-frame findings; human playback judgment remains pending.

![Original left; anchor interpolation right](../exports/turbo-smoothing-v001/compare-interpolation/preview.mp4)

The largest adjacent-frame RGB difference at 384×256 decreases from 16.29 to 7.12 intensity units. Mean change remains similar (4.33 versus 4.24). This diagnostic helped select review windows; it measures pixel changes, not perceived flicker or artistic quality.

Outputs: `../exports/turbo-smoothing-v001/`. Existing accepted control remains in its original location. If neither control addresses abrupt changes adequately, retain three sampling intervals and investigate starting noise / noise evolution / sampling settings next.

## Cadence result

Completed 17 recurrent repaints at cadence 2. Compared with the 11-repaint control, architecture grows more quickly and the shapes diverge further by the end. The flame remains recognizable, but at the inspected boundary around second two, its tip, surface pattern, surrounding openings and tower details still redraw substantially. This does not establish a smoother morphing recipe. Assistant recommendation: keep cadence 3 as the control and move the next investigation to diffusion noise while retaining three sampling intervals. Human playback preference is pending.

![Cadence 3 left; cadence 2 right](../exports/turbo-smoothing-v001/compare-cadence/preview.mp4)

The same small-image pixel diagnostic gives mean adjacent change 5.09 and maximum 16.80, versus 4.33 and 16.29 for cadence 3. More repaints did not reduce the largest measured discontinuity in this clip. These values are not a perceptual score, and the two generated trajectories differ. Five overview samples, every delivered frame around 1.875–2.125 seconds, and full-size images immediately before/after second two were inspected.

## Execution and preservation

- Exact same opening pixels, prompt, Krea FP8 weights, Euler sampler, simple scheduler, CFG 1, shift 1.15 and three-interval sigma tail. Starting sigmas remain `[0.6545668244, 0.5128440857, 0.3109010756, 0]`. Seed starts at 491744 and increments once per repaint; additional repaint counts change its assignment over time.
- ComfyUI 0.34.0 at `12d5279438bfefc058a269eae805ceab6047777f`, Torch 2.10.0+cu128. The new branch used the cache trial's warm RTX 4090, versus the control's L40S. The retained runtime has OpenCV 4.13.0, Pillow 12.2.0 and NumPy 2.5.0. Selected archived warps matched local reconstruction within the established cross-platform tolerance. This is a practical recipe comparison, not bitwise hardware equivalence.
- Median graph execution: 4.213 seconds; approximately 7.5 seconds per complete recurrent iteration including warping, collection and checkpointing. No model download or ComfyUI reinstall in this task.
- The runner initially failed before submission because its legacy spatial-helper import chain eagerly imports `boto3`. Installed the repository dependency into the retained virtual environment and preflighted the actual runner before relaunch. Failure log preserved; central friction record **AF-20260910-002540**. Legacy import coupling remains a future cleanup item. Archive extraction also rejected Mac ownership metadata on the network mount; all 62 source-file hashes verified despite those metadata warnings.
- Verified all 17 parent/input/output hashes, requested/executed graphs and successful histories; sampled spatial warps; all 36 source-frame hashes; 72 delivery frames at 24 fps for exactly three seconds. Each new output is the next iteration's input after warping. Both comparisons share the original opening and duration.
- All 318 archived files, including the 34 remote input/output images and 17 run receipts, downloaded and hash-verified. Archive SHA256: `a77a01ba44f6126acb6762937b1a7cd909ddf49088f82da2af166419f5ec75fc`. Original control, every new generation, raw/final RIFE frames, individual clips and comparisons remain local. No prior generation was replaced.
- The handed-off RTX 4090 Pod was deleted after verified downloads and an empty queue. Live Pod listing is empty. The authorized 50 GB `deforum-models` volume remains in EU-RO-1; retained storage still costs approximately $3.50/month. Trial files and shared model/runtime files were preserved.

Individual videos: [interpolation](../exports/turbo-smoothing-v001/interpolation/preview.mp4), [cadence 2](../exports/turbo-smoothing-v001/cadence-2/preview.mp4), [original cadence 3](../exports/turbo-transitions-v001/tail-3/preview.mp4). [Runner](turbo_smoothing.py), [verification and comparison](turbo_smoothing_review.py). Private execution and cleanup receipts: `apps/deforum/work/turbo-smoothing-session/`.
