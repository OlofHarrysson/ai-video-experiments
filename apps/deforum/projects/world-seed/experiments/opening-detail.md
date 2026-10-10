# Opening detail: prompt first, sampling second

Authorized 2026-10-10 after Olof noticed detail changing immediately after the opening. Compare two seconds of the original jungle approach at native 1536×1024, 24 fps and the established 4.5× delivery timing. Preserve the complete thirty-second v004.

| Case | Text conditioning | Repaint sampling |
| --- | --- | --- |
| Baseline, p01 through source204 | Existing short travelling descriptions | Three Euler intervals |
| d01-full-prompt | Complete original opening description throughout | Same three Euler intervals |
| d02-full-prompt-six-steps | Identical to d01 | Six Euler intervals, subdividing each existing interval at its midpoint |

All cases share the exact original opening, the camera path, eighteen painting positions, seed schedule, noise schedule, model, text encoder, VAE, CFG and finishing. The first comparison changes only text conditioning; the second changes only sampling resolution. Six steps retain the three-step schedule's original sigma points and start/end noise levels. This is a controlled test of this subdivision, not a universal test of all higher-step schedules.

Initialization remains the warped previous painting followed by partial-noise repaint. There is no additional reference-image conditioning. Recurrent images naturally diverge after the first different repaint, so later comparisons assess evolving outcomes rather than pixel-aligned replicas. Baseline paintings are reused without new inference. Each new case generates seventeen paintings; RIFE only supplies delivery in-betweens.

Inspect the actual paintings for bark, moss, petal veins and the engraved doorway rim, then inspect interpolation windows separately. Prefer detail that remains coherent while moving; edge contrast or unstable speckling alone is not the requested visual richness. Human playback preference decides the selection.

Configurations: [full prompt](configs/d01-full-prompt.json), [full prompt with six steps](configs/d02-full-prompt-six-steps.json). The project runner now validates an explicit sigma-ratio schedule while preserving the default three-interval requirement. Every existing project config passes preflight.

## Results

[Compare all three clips](http://localhost:3028/world-seed-detail) · [Full prompt, three steps](../exports/v002/d01-full-prompt/faster/rife-moving-tail/preview.mp4) · [Full prompt, six steps](../exports/v002/d02-full-prompt-six-steps/faster/rife-moving-tail/preview.mp4)

Assistant judgment: keeping the complete prompt is the clearer improvement. At the final original painting (1.875s), both full-prompt cases retain layered roots, moss, fungi and distant growth; the baseline has become flatter foliage and larger simple decorative shapes. The first repaint still alters fine texture in both alternatives. The full prompt does not solve all detail loss.

The six-step case develops denser vegetation, more leaf veins and an ornamented doorway rim, but also stronger patches of paint/highlight on the petals. It changes the look rather than consistently making every material crisper. Before human review, the assistant provisionally recommended the three-step full-prompt case for its cleaner petal treatment, with six steps as an alternative for denser ornament. Neither establishes the requested meticulous detail in every frame. This is one opening/seed family; it does not establish a universal step count.

## Human review and prompting audit — 2026-10-10

Olof finds the three results very similar and tentatively prefers the original. Retain the original as the working choice; the assistant's preference for the fuller prompt did not predict his playback preference. He clarifies that the question is about style and quality language, including possible prefixes or suffixes, rather than simply adding more scene content. He requests the exact prompts and model-specific prompting research.

The executed opening and first-repaint graphs both load `krea2_turbo_fp8_scaled.safetensors`, the Qwen3VL encoder and Qwen Image VAE. Their text matches [the opening configuration](configs/o1-jungle.json) and [the original travelling schedule](configs/p01-the-root-bridge.json). There is no automatic prompt expansion in these graphs. Both new comparisons retain the exact long opening prompt; d02 changes sampling only. The original opening asks for “Lavish maximalist surreal oil painting” and “convincing luminous paint”; the first travelling prompt asks for “Lavish surreal oil painting” and “finely detailed roots and moss.” Retaining more scene description did not isolate the effect of changing medium or surface-rendering language.

Official sources rechecked on 2026-10-10:

- [Krea's Turbo prompting guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md) recommends natural-language descriptions, favors detailed prompts while demonstrating concise ones, and explicitly identifies its examples as Turbo outputs. Examples specify medium, lighting, texture and composition; it does not establish a special quality-prefix syntax.
- [The linked official expansion instructions](https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt) preserve subjects and spatial relationships, avoid unsupported additions, retain the requested medium, and lightly polish already-detailed prompts. This supports refining the intended appearance without inventing more objects.
- [Krea's broader hosted-product guide](https://www.krea.ai/blog/explorative-prompting-krea-2) recommends broad exploration followed by style, medium, lighting and composition constraints. Its exploration workflow is not a validated recipe for our recurrent partial-noise repaints.

The project had already consulted the official Turbo guide in [earlier prompting research](../../../../../docs/research/prompting-for-feedback.md). The present comparison tested retention of the complete description and sampling subdivision; it did not test a crisp digital-art treatment. The oil-painting wording may contribute to the surface aesthetic, but this is a hypothesis, not an isolated cause of blur. A possible next comparison would retain the original scene and sampling while varying only rendering language. No new generation or prompt configuration was changed during this audit.

## Screening and validation

All 34 new paintings were viewed in consecutive sheets. Native first repaints and final paintings were compared with the baseline. Each new RIFE opening pair was inspected at every displayed frame (0–0.125s); the baseline pair is byte-identical to the previously inspected film. Matched close windows inspected every delivered frame at 0.875–1.125s and 1.75–1.958333s for baseline/full prompt and three/six steps. The bridge, doorway and principal plants remain connected in these windows, while small features continue to change. Frame inspection does not establish normal-speed human rhythm preference.

Both new cases and the reused baseline pass generation/provenance validation. The first warped input has identical decoded pixels across all three cases; PNG byte encoding differs between the historical local and new remote runs. Seeds, noise levels and camera schedules match; six-step sampling contains every original three-step sigma point. All three deliveries pass full decode, timing, source retention, hashes and moving-tail checks: 48 frames, 24 fps, two seconds, eighteen original paintings, native 1536×1024. All RIFE settings are identical. [Controlled-input checks](opening-detail-check.json) · [Execution and delivery hashes](opening-detail-execution.json).

All 484 remote files are hash-verified locally. After confirming an empty queue, 68 verified ComfyUI duplicates were removed and the owned Pod was deleted. A live follow-up found no Pods; the shared model volume remains. Estimated GPU cost is $0.13, excluding storage. No separate external media backup is configured. The original thirty-second film remains unchanged.

The local reviewer serves all three exact MP4 hashes and supports range requests; its selected IDs, labels, 48-frame timelines and generation roles are verified. The three existing server tests pass. The player layout was unchanged; no new browser interaction test was performed. The reviewer is left running for Olof's comparison.

The incremental transfer initially retained an unfinished submission receipt because it skipped existing filenames. Content-hash synchronization refreshed the receipt; local validation then passed. The final complete inventory verification passed. This workflow issue is recorded as AF-20261010-181147.

## Reproduction

From `apps/deforum/`, run `projects/world-seed/experiments/film.py` with `uv run --locked python`: `plan`, `render` with an owned deployment receipt, and `check` for each case through source204. The six-step schedule is explicit in its config. Run the existing `finish.py CASE pair --version v002`, inspect, then `full` and `tail`. The preserved baseline uses `finish.py p01-the-root-bridge STAGE --through-frame 204`. The reviewer session is `media_review/sessions/world-seed-detail.json`; build with `media_review.build(..., local=True)` for the allowlisted local route.
