# Modern model study

Test FLUX.2 Klein 4B distilled and Krea 2 Turbo for controllable, surreal animation. Each model generates its own opening and all subsequent repaints. Use direct twist motion and cadence 3; model-specific prompts, sampling recipes and bounded clip lengths are recorded per experiment.

Two three-second auditions are complete: [Krea and Klein results](experiments/pod-results.md). Each model generated its own opening and feedback. Olof finds both interesting but reports jitter and doubled images in Krea; he has not selected a winner. All 32 generated images and both clips are local; the Pod is deleted. The earlier serverless attempt stopped before inference.

Current follow-up: [initialized feedback with optional reference conditioning](experiments/additive_reference.md). Both versions keep the warped previous image as the diffusion starting point. One also receives the previous generated frame as a separate reference. Same-model openings, cadence 3 and no blending keep this focused on the additional conditioning.

All four two-second clips and both labeled comparisons are complete. Klein with reference is the assistant's candidate for controlled motion; Krea supplies stronger morphing but still changes structure and fades detail. Human playback feedback is pending. All 34 generated images and 88 remote input/output files are preserved locally; the Pod and storage are deleted.

Earlier [text-only/reference sequences and no-blend reconstructions](experiments/conditioning.md) are preserved, but their new sequences omitted previous-image sampling initialization and did not test Olof's intended combined mechanism. The misunderstanding is recorded in the collaboration agreement.

## Experiments

- [Feedback plus optional reference](experiments/additive_reference.md): matched single-step probes and short feedback comparisons for Klein and Krea.

- [Text-only and native-reference comparison](experiments/conditioning.md): no-blend reconstructions and supported input-mode tests for both models.

- [Pod results](experiments/pod-results.md): playable clips, prompting comparisons, temporal limitations and verified cleanup.

- [Audition](experiments/baseline.md): opening images, warped-frame probes and bounded feedback clips.

[References](references/README.md) · [runs](runs/README.md) · [cuts](cuts/README.md) · [exports](exports/README.md)

Follow the [working convention](../../../../docs/workflow.md).
