# Modern model study

- [Krea lower repaint strengths](experiments/krea-low-repaint.md) — 0.10/0.18/0.24 with the preserved cathedral feedback loop.

Test FLUX.2 Klein 4B distilled and Krea 2 Turbo for controllable, surreal animation. Each model generates its own opening and all subsequent repaints. Use direct twist motion and cadence 3; model-specific prompts, sampling recipes and bounded clip lengths are recorded per experiment.

New execution convention: **24 fps source and delivery, time-based spatial motion, RIFE on by default**. The [timing migration experiment](experiments/timebase24.md) preserves the accepted baseline as cadence 6 (a repaint every 0.25 seconds). Existing cadence studies retain their historical labels and files. Use the shared `FeedbackTiming()` defaults for future runs; keep RIFE outside recurrent generation.

Latest experiment: [repaint every 0.5s versus 1s](experiments/repaint-intervals.md), two six-second shots with the same Krea recipe and RIFE settings. Both run at native 24 fps (cadence 12/24). All sixteen fresh diffusion calls and finished outputs are local and verified. The one-second branch is the assistant's calmer audition candidate; half-second repainting develops more structure. Human playback judgment is pending. Owned GPU deleted; model cache retained.

Current creative baseline: Olof prefers the [three-step continuation with RIFE](experiments/turbo-smoothing.md), calling interpolation substantially better and cadence 2 worse. The latest [cadence 3, 7, 10 and 15 comparison](experiments/cadence-slow.md) is complete both raw and with the same RIFE settings. All clips retain their original three-second timing; all diffusion anchors and raw outputs are preserved. RIFE spreads the redraws over time with some softened/doubled fine details. Cadence 10 is the assistant's middle-ground audition; human playback verdict is pending. The earlier [cadence 4 and 5 study](experiments/cadence-spacing.md) remains preserved. Report seconds per repaint alongside source-motion and delivery FPS. The interpolation follow-up ran locally without new diffusion or cloud compute.

The earlier [four cathedral clips](experiments/cathedral-feedback.md) compared two strengths per model. Olof found Krea still too flickery, prompting the lower-strength follow-up.

The [opening artwork audition](experiments/opening-art.md) completed an official Krea setup control and six reference-led openings. The assistant recommends Krea’s living cathedral, with Klein’s darker cathedral as an alternative; Olof calls both cathedral openings really good; he subsequently selected Krea for continued animation. All seven images are local and the Pod/storage are deleted. No animation was tested in this round.

The preceding [initialized feedback with optional reference conditioning](experiments/additive_reference.md) retained the warped previous image as the diffusion starting point, with a second branch also receiving the previous generated frame as a separate reference. Its 34 generated images, four two-second clips and both comparisons are preserved locally. Olof finds Klein more consistent but less interesting than the SDXL/reference art, and rejects Krea including its opening; this prompted the still-image audition. That Pod/storage are also deleted.

Earlier [three-second auditions](experiments/pod-results.md) produced 32 images and two clips. Olof found both models interesting but reported Krea jitter and doubled images. The subsequent [text-only/reference sequences and no-blend reconstructions](experiments/conditioning.md) are preserved, but their new sequences omitted previous-image sampling initialization and did not test his intended combined mechanism. The misunderstanding is recorded in the collaboration agreement. The earlier serverless attempt stopped before inference.

## Experiments

- [Latent feedback](experiments/latent-feedback.md): completed 24-cycle comparison; removing repeated VAE encoding does not prevent flattening.

- [Repaint degradation diagnosis](experiments/repaint-diagnosis.md): 24-cycle no-motion and VAE controls, repeated warps, and one matched Lanczos animation.

- [Cathedral feedback](experiments/cathedral-feedback.md): two repaint strengths per model, motion-only previews and synchronized comparisons.

- [Opening artwork](experiments/opening-art.md): normal Krea setup control and richer, reference-led concepts for both models.

- [Feedback plus optional reference](experiments/additive_reference.md): matched single-step probes and short feedback comparisons for Klein and Krea.

- [Text-only and native-reference comparison](experiments/conditioning.md): no-blend reconstructions and supported input-mode tests for both models.

- [Pod results](experiments/pod-results.md): playable clips, prompting comparisons, temporal limitations and verified cleanup.

- [Audition](experiments/baseline.md): opening images, warped-frame probes and bounded feedback clips.

[References](references/README.md) · [runs](runs/README.md) · [cuts](cuts/README.md) · [exports](exports/README.md)

Follow the [working convention](../../../../docs/workflow.md).
