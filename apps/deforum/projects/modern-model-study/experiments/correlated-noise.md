# Fresh versus gradually changing noise

Completed 2026-09-13. Olof likes the correlated branch's mosaic-like colors and finds the style interesting for possible later use, while agreeing it misses the current preservation goal. Preserve it as a liked creative effect. Assistant review favors independent noise for preserving this scene; correlation 0.85 is not a new default.

Two stationary four-second continuations start from the same saved Krea canyon-city painting and its unchanged city prompt. Both retain RGB recurrent initialization, CFG1, Euler, sigmas `[0.6, 0.512844085693, 0.310901075602, 0]`, four paintings/s (cadence6), 24 fps and identical RIFE finishing. Each has the opening plus fifteen fresh paintings. No warping, masks, reference conditioning or image blending is added.

- Control: independent standard Gaussian noise at each repaint.
- Treatment: `epsilon[n] = 0.85 * epsilon[n-1] + sqrt(1-0.85^2) * eta[n]`, with independent standard Gaussian innovations. Marginal variance remains one in theory. No empirical per-frame normalization. All innovations use the same seed sequence as the control; the first repaint has identical noise and input in both cases.

The [noise helper](../../../noise_sequence.py) exposes one small ComfyUI NOISE node; sampling uses core CFGGuider/SamplerCustomAdvanced. Before the study, a real matched-input parity check must reproduce SamplerCustom's pixels exactly. The custom node records actual noise and input latents. Core AddNoise/VAEDecode provides selected approximate noisy-latent previews, outside feedback. These are diagnostic decodes, not literal RGB noise or a depiction of the model's internal view.

The opening is `refresh-rate-v001/two-current/anchors/0144.png`, after several repaints already using the city prompt. This avoids introducing a new subject prompt at the beginning of a preservation test. Stationary noise correlation does not establish behavior during moving or intentionally transforming scenes. Historical fixed-seed SDXL findings do not settle partial correlation with Krea.

Execution budget: up to $1 within the existing $10 session (previous cumulative estimate $2.52). Reuse the retained EU model cache on a short-lived Pod, archive and hash-verify every output/noise tensor, then delete owned compute and scratch. Keep the model volume. Run [correlated_noise.py](correlated_noise.py) through prepare, parity, render; preserve raw paintings and show matched RIFE videos in the linked local reviewer.

## Findings

The control keeps a restrained brass/copper palette and shaded volumes, although small roofs and windows still evolve. In the correlated branch, turquoise/orange patches spread across the large ring and rooftops by 0.75s. By 1.75s, flat yellow, blue and red patterns are prominent; by 3.75s the city has a bright mosaic-like treatment. Much of the large layout persists, but the original shading and color identity do not. This fails the intended preservation test even if the alternate style is visually interesting.

Noise standard deviation stays approximately 0.998–1.002 in both branches. Mean adjacent-noise correlation is 0.00013 in the control and 0.84992 in the treatment. The actual recorded arrays also satisfy the intended recurrence numerically. The failure is not an accidental increase in noise amplitude. Mean absolute change between paintings is similar: 0.0399 versus 0.0407 on normalized RGB; that aggregate is not a video-quality score.

A diagnostic correlation between the added noise and the current raw input latent grows to roughly 0.14 in the treatment, while remaining near zero in the control. This is compatible with recurrent reinforcement of noise-related structure, but does not establish the cause of the visual drift. Constant marginal noise variance does not guarantee independence from the image being repainted. [PYoCo](https://arxiv.org/abs/2305.10474) trained a video model with correlated priors; it does not validate this inference-only intervention in Krea.

Retain the independent-noise recipe. This result covers one scene, sigma 0.6 and correlation 0.85; it does not rule out milder correlation or other mechanisms. No movement or intentional prompt switch was tested, and no follow-up GPU experiment is implied.

## Human feedback and follow-up questions

Olof calls the video “pretty cool,” specifically likes the mosaic-like colors, and says it may have a later use despite missing this test's goal. Keep that aesthetic preference separate from preservation performance. He asks to understand noise tensors, internal sampling steps, latent recurrence and an image-to-noise encoding idea. [Noise and latent continuity](../../../../../docs/research/noise-and-latent-continuity.md) answers those questions from the recorded arrays, current sampler source and inversion research; its next experiment is a proposal only.

## Verification and delivery

The live native SamplerCustom versus CFGGuider/SamplerCustomAdvanced comparison was pixel-identical. Both branches also have identical first-repaint pixels. All thirty recurrent jobs have verified parent/upload/output hashes, exact executed graphs, unchanged text/CFG/sigmas, and actual noise arrays. Two additional parity jobs are archived. [Verification and review helper](correlated_noise_review.py).

The 567-file archive is local and hash-verified. All 133 owned ComfyUI media/tensor files, the session scratch directory and the temporary installed noise node were removed; the owned RTX 4090 Pod was deleted and absence confirmed. The authorized model volume remains. Estimated round cost is at most about $0.15 including a $0.03 disk allowance, with a cumulative original-session estimate of $2.67/$10; this is an estimate, not posted billing. Setup included a corrected archive ownership command; the process incident is logged as AF-20260913-185946.

Exports: `../exports/correlated-noise-v001/`. The two `section-016/rife/preview.mp4` deliveries use sixteen paintings, four seconds, 24 fps and the same RIFE 4.25 scale 1. Their final quarter-second holds the last stationary painting. Recorded noise fields are under `diagnostics/`; selected `noise-walkthrough-*.jpg` sheets compare previous painting, approximate decoded noisy latent and next painting. Grayscale noise movies show actual channel-zero values with a fixed -3 to +3 scale; they are not guide videos or RGB grain overlays.

Both MP4s fully decode and all sixteen painting positions plus final holds match their original PNG pixels before encoding. Assistant review includes matched source paintings from opening to ending, six timestamp-matched delivery samples per video, and every delivered frame from 0.5–0.75s. RIFE spreads the transition but retains the treatment's underlying color/style drift. These sampled-frame findings do not substitute for Olof's playback preference.

Human review: [local reviewer](http://localhost:3028/), saved [session](../../../media_review/sessions/correlated-noise.json). Open on the two artwork videos; optional noise-field videos are in the dropdowns. All earlier generations remain preserved.

Browser verification: both artwork videos loaded and played to frame95 together, painting stepping reached frame6/painting1, and both noise-field videos loaded and played through. The complete side-by-side layout and shared controls fit the inspected 1280×720 viewport. Noise-only clips intentionally have no certified painting metadata. Devrun's `media-review` service remains ready at the verified URL for Olof's review.
