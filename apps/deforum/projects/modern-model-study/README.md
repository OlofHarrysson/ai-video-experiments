# Modern model study

Latest: [three parallel directions](experiments/three-directions.md) compares stronger sustained motion and a simpler Oracle prompt against a fresh control, plus SPEED versus RIFE on saved endpoint pairs. All media is local and verified, and the shared Pod is deleted. Assistant recommends the stronger movement, especially seconds 5–9; late expansion needs framing control. Simpler prompting changes the face without clearly solving redraws. SPEED adds artifacts in this audition; retain RIFE. Human feedback is pending.

- [Krea lower repaint strengths](experiments/krea-low-repaint.md) — 0.10/0.18/0.24 with the preserved cathedral feedback loop.

Test FLUX.2 Klein 4B distilled and Krea 2 Turbo for controllable, surreal animation. Each model generates its own opening and all subsequent repaints. Use direct twist motion and cadence 3; model-specific prompts, sampling recipes and bounded clip lengths are recorded per experiment.

New execution convention: **24 fps source and delivery, time-based spatial motion, RIFE on by default**. The [timing migration experiment](experiments/timebase24.md) preserves the accepted baseline as cadence 6 (a repaint every 0.25 seconds). Existing cadence studies retain their historical labels and files. Use `FeedbackTiming(repaint_seconds=1)` for the selected one-second pacing; keep RIFE outside recurrent generation.

Latest scene-transition study: [Oracle noise and steps](experiments/oracle-steps.md) compares 0.4 with 3/9 sampling intervals and 0.6 with 3/1, switching to Oracle at second two of twelve. All 44 repaints and four twelve-second RIFE videos are local and verified; owned Pod deleted. Assistant painting review favors 0.6/3 for a clear face transformation; low-noise extra steps do not recover depth. Olof finds both high-noise cases interesting and agrees that adding steps at low noise did not solve the problem.

Earlier scene-transition study: [two prompts and four noise levels](experiments/prompt-noise.md) uses cathedral → mechanical moth halfway through eight seconds. Assistant finds the strongest partial transformation at 0.6; lower levels mostly preserve the old scene. No complete moth appears in four new-prompt repaints, and Olof now requests Oracle instead of the moth. All 28 repaints are local and verified; owned Pod deleted.

Earlier diffusion study: [starting noise](experiments/starting-noise.md) compares 0.655/0.62/0.60/0.56 with three sampling intervals and identical timing/interpolation. All twenty repaints are local and verified, and the owned Pod is deleted. Human choice is pending; the accepted 0.655 baseline remains preserved.

Earlier local follow-up: [RIFE motion-estimation scale](experiments/rife-scale.md) is complete. Half-scale is the assistant's tentative candidate for less doubled later detail; some ghosting remains. Olof finds no strong preference and parks scale tuning. Both videos preserve the same paintings and warp-only tail, with no new diffusion or cloud work. RIFE scale 1.0 remains the default.

Selected pacing: [repaint every 0.5s versus 1s](experiments/repaint-intervals.md), two six-second shots with the same Krea recipe and RIFE settings. Both run at native 24 fps (cadence 12/24). All sixteen fresh diffusion calls and finished outputs are local and verified. **Olof selects the one-second branch as better and more morphing.** It is the current pacing baseline. Owned GPU deleted; model cache retained.

Earlier creative baseline: Olof prefers the [three-step continuation with RIFE](experiments/turbo-smoothing.md), calling interpolation substantially better and cadence 2 worse. The latest [cadence 3, 7, 10 and 15 comparison](experiments/cadence-slow.md) is complete both raw and with the same RIFE settings. All clips retain their original three-second timing; all diffusion anchors and raw outputs are preserved. RIFE spreads the redraws over time with some softened/doubled fine details. Cadence 10 is the assistant's middle-ground audition; human playback verdict is pending. The earlier [cadence 4 and 5 study](experiments/cadence-spacing.md) remains preserved. Report seconds per repaint alongside source-motion and delivery FPS. The interpolation follow-up ran locally without new diffusion or cloud compute.

The earlier [four cathedral clips](experiments/cathedral-feedback.md) compared two strengths per model. Olof found Krea still too flickery, prompting the lower-strength follow-up.

The [opening artwork audition](experiments/opening-art.md) completed an official Krea setup control and six reference-led openings. The assistant recommends Krea’s living cathedral, with Klein’s darker cathedral as an alternative; Olof calls both cathedral openings really good; he subsequently selected Krea for continued animation. All seven images are local and the Pod/storage are deleted. No animation was tested in this round.

The preceding [initialized feedback with optional reference conditioning](experiments/additive_reference.md) retained the warped previous image as the diffusion starting point, with a second branch also receiving the previous generated frame as a separate reference. Its 34 generated images, four two-second clips and both comparisons are preserved locally. Olof finds Klein more consistent but less interesting than the SDXL/reference art, and rejects Krea including its opening; this prompted the still-image audition. That Pod/storage are also deleted.

Earlier [three-second auditions](experiments/pod-results.md) produced 32 images and two clips. Olof found both models interesting but reported Krea jitter and doubled images. The subsequent [text-only/reference sequences and no-blend reconstructions](experiments/conditioning.md) are preserved, but their new sequences omitted previous-image sampling initialization and did not test his intended combined mechanism. The misunderstanding is recorded in the collaboration agreement. The earlier serverless attempt stopped before inference.

## Experiments

- [Next diffusion and interpolation research](../../../../docs/research/diffusion-and-interpolation-next.md): lower starting sigma with three sampling intervals recommended first; SPEED is a newer interpolation candidate; its completed bounded audition is recorded in [three directions](experiments/three-directions.md).

- [RIFE motion-estimation scale](experiments/rife-scale.md): the same six paintings, comparing full-scale and half-scale interpolation at full-resolution 24 fps.

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
