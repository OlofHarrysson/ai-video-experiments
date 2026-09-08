# Modern model study

Test FLUX.2 Klein 4B distilled and Krea 2 Turbo for controllable, surreal animation. Each model generates its own opening and all subsequent repaints. Use direct twist motion and cadence 3; model-specific prompts, sampling recipes and bounded clip lengths are recorded per experiment.

Two three-second auditions are complete: [Krea and Klein results](experiments/pod-results.md). Each model generated its own opening and feedback. Olof finds both interesting but reports jitter and doubled images in Krea; he has not selected a winner. All 32 generated images and both clips are local; the Pod is deleted. The earlier serverless attempt stopped before inference.

Latest follow-up: [five text-only/reference sequences and no-blend reconstructions](experiments/conditioning.md) are complete. Klein retains layout through native reference conditioning but has color drift; Krea’s style adapter changes structure and fades the palette. All new outputs are local and the temporary Pod is deleted.

## Experiments

- [Text-only and native-reference comparison](experiments/conditioning.md): no-blend reconstructions and supported input-mode tests for both models.

- [Pod results](experiments/pod-results.md): playable clips, prompting comparisons, temporal limitations and verified cleanup.

- [Audition](experiments/baseline.md): opening images, warped-frame probes and bounded feedback clips.

[References](references/README.md) · [runs](runs/README.md) · [cuts](cuts/README.md) · [exports](exports/README.md)

Follow the [working convention](../../../../docs/workflow.md).
