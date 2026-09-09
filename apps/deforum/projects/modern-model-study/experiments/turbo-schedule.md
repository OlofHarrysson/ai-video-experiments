# Turbo schedule tail versus smaller updates

Olof authorizes the assistant to lead the next experiments and reports little visible difference between RGB and latent feedback. Keep Krea, the accepted cathedral opening and the feedback loop. Test a specific schedule hypothesis before choosing another model or adding latent-space motion.

## First comparison

Two 24-cycle no-motion branches with direct latent feedback, one opening VAE encode and observation-only decoding. Same model assets, prompt, seed sequence, Euler sampler, CFG 1 and starting noise. Core ComfyUI nodes only.

- **Turbo tail:** generate the normal eight-step simple schedule, keep its final interval (sigma approximately 0.311 to zero).
- **Eight small updates:** generate a 64-step simple schedule, keep its final eight intervals, starting at exactly the same sigma.

Verify both actual sigma lists on the pinned remote runtime before inference. This changes step count and intermediate noise levels together while matching the initial noise coefficient and random noise. It compares schedule recipes, not distillation in isolation. The normal full-generation recipe does not guarantee that its tail works well for repeated editing.

Review early and late states, plus matched playback. If one branch materially preserves useful shading/detail, test it with a short Lanczos twist using ordinary warped-image feedback and cadence 3. Otherwise record the negative result and choose a bounded follow-up based on the observed failure. Do not promote a no-motion result to an animation-quality claim.

Sources: [Krea's inference code](https://github.com/krea-ai/krea-2/blob/main/sampling.py), [pinned ComfyUI custom sampler nodes](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py). The Krea schedule uses fixed shift 1.15 for the distilled checkpoint. The actual sigma values, executed graphs and every generated image will be preserved.

## Status

Complete: 48 diagnostic states and 22 motion repaints. The single Turbo interval is the assistant-selected candidate; human playback feedback is pending. All media is local and owned cloud resources are deleted.

## Adaptive motion follow-up

The matched cycle-24 review shows more retained broad shaded arches with the single Turbo interval, versus flatter decorative patterns with eight small intervals. Both still lose some richness. This is enough to justify the planned motion check, not a declaration of solved quality.

Run a three-second, 1536×1024 Lanczos twist at twelve source fps and cadence 3: eleven repaints per branch. Each repaint initializes from the warped previous generated RGB image, encoded through the VAE as usual. Compare the same two sigma schedules with the same opening and seed sequence. Intermediate frames only warp the preceding generated anchor; no blending, reference conditioning or RIFE. The two motion branches match each other; this RGB feedback differs deliberately from the no-motion latent diagnostic.

## Verified schedule and scope

Both branches begin at sigma **0.3109010756**, then end at zero. The single-interval branch uses `[0.3109010756, 0]`. The subdivided branch uses `[0.3109010756, 0.2795118093, 0.2463647723, 0.2113080621, 0.1739266068, 0.1345047653, 0.0925964117, 0.0479586162, 0]`. Lists were evaluated against the actual pinned remote model sampling configuration before inference.

This is one final interval of the normal eight-step schedule, not a one-step full image generator. The comparison changes both evaluation count and intermediate noise levels. It does not separately identify which matters, establish that distillation causes degradation, or test a non-distilled checkpoint. The start noise differs from the earlier denoise-0.10 experiment; compare the two matched new branches with each other.

Both use Krea Turbo FP8, Euler, simple scheduling, CFG 1, model shift 1.15, the accepted 1536×1024 cathedral opening, unchanged cathedral prompt and seeds 491732 onward. ComfyUI 0.34.0 commit `12d5279438bfefc058a269eae805ceab6047777f`, PyTorch 2.10.0+cu128, L40S 48 GB. Model, text encoder and VAE bytes were verified against the existing pinned manifest. No extra model pack or custom sampler node was added.

## No-motion result

The single Turbo interval retains more broad shaded arches and material depth. Eight smaller intervals produce flatter, more decorative patterned surfaces. Both still lose richness across 24 cycles. The direct latent chain removes repeated VAE encoding from this diagnostic, but its initial encoding and observation decoding remain.

![Eight small updates on the left; Turbo final step on the right](../exports/turbo-schedule-v001/comparison/preview.mp4)

Playback shows four repaint cycles per second, not a camera animation. Reviewed cycles 0, 1, 4, 11 and 24, including full-resolution final comparisons and cropped architectural details.

| Grayscale standard deviation | Opening | Cycle 11 | Cycle 24 |
| --- | --- | --- | --- |
| Turbo final interval | 56.15 | 46.41 | 38.18 |
| Eight small intervals | 56.15 | 42.34 | 30.57 |

These measurements describe contrast, not aesthetic quality. The visible difference supports the motion follow-up; it does not prove that the single interval is a universal better setting.

## Motion result and recommendation

**Use the single Turbo interval as the next assistant-selected working baseline.** Its three-second Lanczos twist retains a cleaner central flame and broad curved architectural shading. The eight-small-update control becomes more mottled, with surface patterns breaking up the flame and arches. Both retain the intended twist. The single interval still simplifies detail and loses some opening richness; it has not solved long-duration quality or earned a human taste preference yet.

![Same twist: eight small updates left, Turbo final step right](../exports/turbo-schedule-motion-v001/comparison/preview.mp4)

The two individual versions are preserved: [Turbo final step](../exports/turbo-schedule-motion-v001/turbo-tail/preview.mp4) and [eight small updates](../exports/turbo-schedule-motion-v001/small-updates/preview.mp4). Each is three seconds at twelve source fps, delivered at 24 fps by repeating frames. Cadence 3 means eleven generated anchors after the shared opening. There is no RIFE or frame blending. Warped generated anchors feed each next repaint; motion was not pre-rendered and then sparsely replaced.

Assistant review inspected six evenly spaced video samples, every delivered frame around 1.9–2.15 seconds with matched comparisons, and the final source-frame comparison at larger scale. Sampled visual evidence supports cleaner shapes and shading, but does not establish an exhaustive flicker assessment or Olof's playback preference.

The next useful creative test is a modestly longer shot with this recipe and an intentional transition from twist to regional expansion. Hold sampling fixed to find its practical duration limit and judge whether the morphing remains interesting. Do not add latent warping or switch models in that same comparison. If quality still fails too soon, an undistilled Krea comparison remains a separate hypothesis.

## Execution, verification and cleanup

**24 successful requests produced 70 images:** two 24-cycle no-motion graphs and twenty-two motion repaints. Both exact schedules, all requested/executed graphs, opening/parent/input/output hashes, seed progression and successful history states are verified. Motion verification also reconstructs selected Lanczos warps, checks a cadence boundary and neighboring frames, and validates delivery frame counts. The two motion graphs differ only in schedule construction and output prefix; the no-motion graphs likewise match apart from those fields.

No-motion graph times were 45.19 seconds for the single interval and 222.53 seconds for eight small intervals, including decoding/saving. Median warm motion-request execution was **1.833 versus 9.360 seconds per repaint**. These are observed request times, excluding setup, network transfer and local warping; the 8:1 evaluation-count difference does not imply an 8:1 end-to-end speedup.

Every generated image, original cloud input/output file, manifest and executed graph is local. The final archive contains **96 hash-verified remote files**, including two bundled files. Archive SHA-256: `ed3cf745890174d69371562f5bb56e6eaddbf2808de79dc20c8963b430ee733d`. Private runtime/model/schedule receipts and archive are under `apps/deforum/work/turbo-schedule-session/`; preserved media is under the project's `exports/`, `runs/` and `references/` directories.

The owned Pod and attached storage were deleted after local verification. Final checks report no Pods, no network volumes and **zero hourly spend**. Observed account balance decreased about **$0.35**, ending at **$41.66**; snapshots are not an itemized final invoice. No persistent serverless or model resources were provisioned.

Runners: [no-motion](turbo_schedule.py), [motion](turbo_schedule_motion.py). Verification and comparison builders: [no-motion](turbo_schedule_review.py), [motion](turbo_schedule_motion_review.py).
