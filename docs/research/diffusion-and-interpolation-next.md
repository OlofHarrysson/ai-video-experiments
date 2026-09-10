# Smaller repaint changes and newer interpolation

Researched 2026-09-10. Source inspection and proposal only: no new inference, dependency installation or cloud resource. Local source snapshots are in `apps/deforum/work/interpolation-diffusion-research/`.

## Human feedback and recommendation

Olof sees no strong difference between the RIFE scale variants. Half-scale might be slightly better, but he wants to park scale tuning. He identifies abrupt differences between paintings as the main remaining issue and asks us to explore diffusion and newer interpolation before recommending the next experiment. Do not record a strong half-scale preference. Keep the existing full-scale default for a controlled diffusion comparison; preserve both scale outputs.

**Start with a smaller starting noise level while retaining three sampling intervals.** Then audition a newer interpolator on the same saved endpoint pairs. This separates making a better sequence of paintings from making better connections between them. Neither is guaranteed to solve the other. The current image model has previous-image initialization but no joint temporal model of the whole movie.

## What the successful sampling change actually was

The [schedule study](../../apps/deforum/projects/modern-model-study/experiments/turbo-schedule.md) compared one native final interval with eight subdivisions covering the same low-noise range. Both began at sigma 0.3109010756. The eight-update control used the last eight intervals of a 64-step schedule, not a full eight-step text-to-image generation. The native interval retained quality better in those experiments. This does not isolate distillation as the cause.

The subsequent [tail comparison](../../apps/deforum/projects/modern-model-study/experiments/turbo-transitions.md) tested the last one, two and three intervals of the ordinary eight-step schedule. Three restored richer detail but also started at a higher noise level. Thus step count, starting noise and update sizes changed together. Olof selected three for its richer detail. Our present tail is:

`[0.6545668244, 0.5128440857, 0.3109010756, 0]`

Call this a **three-step schedule tail**, or the final three sampling intervals. It initializes each repaint from the warped previous generated image. It does not resume the opening image's original diffusion trajectory.

Krea's official recipe describes an eight-step distilled Turbo checkpoint. Its [sampling code](https://github.com/krea-ai/krea-2/blob/main/sampling.py) fixes the distilled schedule shift at 1.15; its full-generation settings are not a validated recurrent-editing recipe. Our ComfyUI CFG 1 bypasses classifier-free amplification; Krea's own CLI convention uses CFG 0 for unguided Turbo. Do not transfer these numbers between implementations without checking their meanings.

The pinned ComfyUI `Krea2` model selects FLUX sampling, whose CONST initialization mixes the noise and previous latent according to sigma. See [model selection](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py) and [noise scaling](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py). Lowering the starting sigma changes both initialization and the first update's range. Sigma is not the percentage of visible pixels repainted, and lowering it is not an independent noise-only intervention.

## Proposed diffusion experiment

Reuse the accepted six-second shot's opening, prompt, Krea weights, Lanczos motion, incrementing seed sequence, one repaint per second, 24 fps and full-scale RIFE. Each new painting must feed the next repaint. Compare:

| Case | Three sampling intervals | Hypothesis |
| --- | --- | --- |
| Preserved control | 0.6545668 → 0.5128441 → 0.3109011 → 0 | Accepted detail and evolution, with abrupt redraws |
| Milder start | 0.60 → 0.5128441 → 0.3109011 → 0 | Smaller structural changes while retaining the finishing intervals |
| Lower start, only if useful | 0.56 → 0.5128441 → 0.3109011 → 0 | Locate the point where retaining structure starts to flatten the artwork |

First render the 0.60 branch: five new repaints, not a large sweep. Inspect raw paintings as well as identical RIFE finishing. If it flattens, do not blindly push lower; if it retains richness but still redraws too much, test 0.56. These shortened first intervals are experimental, off the native Turbo schedule. They may work worse precisely because the distilled model favors its trained sampling times. Do not describe them as official recommended settings.

Core `SetFirstSigma` already exists in the pinned ComfyUI custom sampler module; no new node pack is needed. It can modify the split tail before `SamplerCustom`. Verify the actual schedule and executed graph before a full branch. Do not merely lower KSampler denoise while keeping eight steps, which previously changed the discretization in a less useful way.

Success means smaller discontinuities without sacrificing shading, fine architectural detail, visible spatial motion or interesting evolution. Compare generated anchors with their **warped inputs** to distinguish repaint change from prescribed motion. Inspect all five repaint boundaries at manageable resolution and selected detail crops. A lower pixel-difference score alone could just indicate blur. Deliver baseline versus the best new branch, with both raw diagnostics preserved.

## What changed in interpolation research

| Candidate | Evidence and practical fit | Decision |
| --- | --- | --- |
| RIFE 4.25 / 4.26 | The [author repository](https://github.com/hzwer/Practical-RIFE) still recommends 4.25 for most scenes; it dates to September 2024 and specifically identifies 4.24+ as suitable for diffusion-video postprocessing. 4.26 exists, but a newer version number is not evidence of better results here. | Keep the verified baseline; park further small scale/version sweeps. |
| GIMM-VFI, NeurIPS 2024 | [Official code and weights](https://github.com/GSeanCDAT/GIMM-VFI) support arbitrary timesteps and perceptually trained variants. RAFT/FlowFormer supply motion estimates. A creator-linked ComfyUI port exists. It is another approach from roughly RIFE 4.25's era, not a 2026 breakthrough. | Practical alternative when exact arbitrary timing is the priority; untested here. |
| BiM-VFI, CVPR 2025 | [Official implementation](https://github.com/KAIST-VICLab/BiM-VFI) targets non-uniform motion and provides weights and arbitrary-time benchmark support. Official environment includes CUDA/CuPy. Source/checkpoint terms restrict use to research/education without permission for commercial use. | Worth a research comparison, but improved physical-motion estimation does not establish better surreal topology changes. |
| **SPEED, July 2026** | [Paper](https://arxiv.org/abs/2607.15585) and [official implementation](https://github.com/bbldCVer/SPEED) provide a pixel-space, one-step diffusion interpolator and a released checkpoint. It synthesizes RGB directly, avoiding an interpolation VAE round trip. Unlike our Krea repaint, it is trained to create an intermediate image conditioned on both endpoints. Official setup targets CUDA. | Most interesting bounded newer-model audition: use several saved difficult endpoint pairs before integrating a whole clip. More inventive filling-in can also introduce inconsistent details. |
| LDF-VFI, CVPR 2026 | [Official code](https://github.com/xypeng9903/LDF-VFI) and [weights](https://huggingface.co/onecat-ai/LDF-VFI) use diffusion over temporal chunks for longer-range coherence. The demo reports approximately 20 GB GPU memory and supports factors 2–16. | Substantial architecture change; defer until simpler tests justify it. Direct 24× interpolation is outside the documented range. |
| ArbInterp, ICLR 2026 | [Paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/36572cc8bb2a939f0d998847cb44776e-Abstract-Conference.html) and [project demos](https://mcg-nju.github.io/ArbInterp-Web/) describe arbitrary-time generative interpolation and segment continuity. A usable official code/checkpoint release was not located in this search. | Watchlist, not a ready installation recommendation. |

None of the inspected benchmark evidence establishes superiority on our one-second-spaced surreal recurrent Krea paintings. Changes in object shape, newly appearing holes and rebuilt architecture are not just ordinary motion/occlusion. Learned synthesis may help, but can also compete with our intended transformation.

## Integration detail that matters

[ComfyUI-Tween](https://github.com/ethanfel/ComfyUI-Tween) currently lists SPEED and LDF-VFI as well as the older pairwise models. This is wrapper-author documentation, not validation in our runtime. Its pairwise target-FPS path is documented as power-of-two oversampling capped at 8× followed by nearest-frame selection. SPEED's native operation is midpoint interpolation. Setting target FPS to 24 for 1 fps paintings therefore does **not** establish 23 independently predicted, correctly timed in-betweens. Do not silently introduce duplicated frames or change motion timing.

For SPEED, first compare exact midpoints from two or three saved pairs against RIFE. A midpoint win is only a viability gate, not a video smoothness result. Any full-clip follow-up must explicitly resolve the timestamp schedule, recursion, stochastic seed behavior and anchor preservation, and test repeated interpolation errors. Preserve 24 fps and one-second repaint timing unless Olof agrees to a diagnostic timing change. No wrapper, model or dependency has been installed during this research. The wrapper notes that SPEED's upstream license was absent when pinned; deployment/redistribution terms remain to be established if that becomes relevant.

## Other diffusion levers, in priority order

1. **Starting sigma with three intervals:** smallest targeted next change, described above.
2. **Noise that changes gradually across repaints:** instead of wholly new Gaussian noise every call, retain a controlled temporal correlation while preserving each frame's noise variance. This is different from numerically adjacent seeds (which do not mean similar noise) and from the rejected fixed-seed SDXL clip. It is an untested Krea hypothesis; fixed spatial noise can anchor texture to the screen. [Go-with-the-Flow](https://arxiv.org/abs/2501.08331) supports the relevance of temporally structured noise, but uses specially prepared warped noise and fine-tuned video models. It is not proof that a direct transplant works in our image-model loop. Ordinary RGB Lanczos warping is not a validated Gaussian-noise transport algorithm.
3. **Different sampler/schedule or Krea's non-distilled model:** potentially useful, but changes more assumptions and can add compute. Keep shift/guidance consistent with the exact checkpoint. The native-tail result is a reason to test carefully, not evidence that all small steps or all distilled models are unsuitable.

Execution follow-up: Olof approved diffusion first and requested several noise levels. The [starting-noise study](../../apps/deforum/projects/modern-model-study/experiments/starting-noise.md) compares a fresh native-tail control with 0.62, 0.60 and 0.56, preserving the recurrent pipeline and interpolation settings. SPEED remains deferred; no new interpolation model has been installed.


Execution update (2026-09-10): the [SPEED audition](../../apps/deforum/projects/modern-model-study/experiments/speed-oracle.md) is now complete on three saved pairs, using isolated dependencies on the shared Pod. Its matched 8 fps diagnostic adds patterned ripples/doubled contours without a convincing overall win; retain production RIFE. This supersedes the deferred status above, without claiming a full 24 fps SPEED comparison.
