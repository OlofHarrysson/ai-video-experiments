# Saved-state replay and perturbation

Completed 2026-09-13 after Olof approved the saved-state probe. Test whether small controlled changes to a known sampling state produce gradual, attractive image changes. This is a single-painting diagnostic; it does not replace or establish a new recurrent animation workflow.

Replay the first independent-noise city repaint from `correlated-noise-v001`, using its actual recorded image latent and noise. Keep Krea Turbo, CFG1, Euler, sigmas `[0.6, 0.512844085693, 0.310901075602, 0]`, prompt and source latent unchanged. Before perturbing, require pixel-identical reconstruction of its archived `0006.png` painting.

Change only the initial noise along one fixed direction: `epsilon(a) = sqrt(1-a²) epsilon_saved + a eta`, with Gaussian direction seed 927182. This keeps theoretical marginal variance one for independent Gaussian endpoints, while moving the complete starting state by `0.6 * (epsilon(a) - epsilon_saved)`. It is an arc rather than a straight line so simple noise averaging does not shrink variance. The source image latent remains fixed. Amount is not starting sigma or a percentage of pixels changed.

First inspect amounts 0, 0.02, 0.06, 0.12 and 0.24. If valid, fill two thirteen-sample paths: 0–0.06 in increments of 0.005, and 0–0.24 in increments of 0.02. Display each over 3.25 seconds at 24 fps, six repeated frames per generated sample. No RIFE, warp, prompt changes, regional masks or pixel blending in the diagnostic. Playback speed reflects traversal through a parameter, not a newly tested production repaint rate.

Inspect full images and matched roof/window crops for crispness, color drift, local changes and abrupt jumps. Record executed workflows, actual noise/latent arrays, output hashes and raw samples. A smooth parameter response here does not establish temporal stability when the previous painting changes or motion is introduced.

Budget: bounded below $1 within the existing $10 session (prior cumulative estimate $2.67). Use one short-lived RTX 4090 and the retained model volume; archive all outputs and remove owned compute, scratch and the experimental node afterward. Preserve prior media and the authorized model cache.

## Results

The zero-change replay matches the archived painting **pixel-for-pixel**, with maximum channel difference zero. Twenty-two unique jobs cover the two paths, sharing their four overlapping samples. Recorded graph/history checks confirm the same input latent and perturbation direction throughout; actual saved noise tensors match the specified arc. The input and noise shape is `[1,16,1,128,192]` for 1536×1024 output.

Assistant inspection of full-scene samples and matched roof crops finds restrained changes in roof edges, windows, patina and highlights. The large circular structure, architecture, bronze palette and shading remain recognizable. The wider path is easier to inspect; the small path is nearly static. Consecutive late samples show modest detail variation without the earlier recurrent test's mosaic drift. These are sampled-image findings, with no human playback verdict yet.

Mean normalized RGB absolute difference from the replay is 0.00608 at amount 0.06 and 0.01591 at amount 0.24. These summarize pixel change, not semantic change or quality. Noise standard deviation stays approximately 0.999. We have demonstrated nearby outputs around one known sampling start, not a general smooth morphing method or preservation over repeated feedback.

## Review

- [Open the local comparison](http://localhost:3028/state-replay): full scene beside a 600×600 roof crop of the same samples. “Smaller changes” is available in either dropdown. Obtain the current base URL from Devrun if the service moves.
- [Wider path](../exports/state-replay-v001/wider/preview.mp4), [small path](../exports/state-replay-v001/small/preview.mp4), and [roof detail](../exports/state-replay-v001/wider/detail/preview.mp4).
- [Overview](../exports/state-replay-v001/overview.jpg), [detail samples](../exports/state-replay-v001/details.jpg), and [consecutive samples](../exports/state-replay-v001/consecutive.jpg).

Each diagnostic has thirteen generated samples, held for six frames each: 78 frames at 24 fps, 3.25 seconds. There is **no RIFE**. The amount increases through a parameter path; every sample restarts from the same recorded latent. These clips do not feed the previous displayed painting into the next sample. This isolation is intentional for the approved diagnostic, not a change to the production feedback loop.

The reviewer labels repeated frames as holds and Shift+arrow skips to the next generated sample. At 1280×720, both complete views and controls were visible without scrolling; keyboard steps reached painting 1/frame 6 and hold/frame 7 in both panels, and linked playback completed at frame 77. Paused labels and this playback check do not establish permanent decoder-level frame locking.

## Verification and resources

[Replay check](../exports/state-replay-v001/replay-check.json), [generation check](../exports/state-replay-v001/generation-check.json), and [delivery check](../exports/state-replay-v001/delivery-check.json) are local. All 351 final archive files passed hash verification. Videos fully decode; frame manifests identify thirteen actual paintings and retain source hashes. Seventeen Python review tests and two JavaScript timeline tests passed.

The owned RTX 4090 Pod `n6vyke2o7jftgb` was deleted after download verification; its 67 owned remote media/tensor files, scratch directory and experimental node were removed. The authorized model volume and the other task's active Pod were preserved. Estimated experiment cost is **$0.25**, including a disk allowance. This is not posted billing and excludes concurrent experiments in the other task.

Implementation: [recorded-noise node](../../../replay_noise.py), [runner](state_replay.py), [verification and review builder](state_replay_review.py), and [review session](../../../media_review/sessions/state-replay.json).

## Interpretation and next decision

Keep the recurrent production recipe unchanged. This result supports a local sensitivity probe, but does not answer how to recover a suitable sampling start for an arbitrary or warped previous painting. Any follow-up must explicitly preserve previous-painting initialization and distinguish saved trajectory information from that changing image input. Reusing this one fixed source across a longer video would lose the intended feedback behavior. Inversion remains unvalidated for Krea and requires separate alignment before implementation.
