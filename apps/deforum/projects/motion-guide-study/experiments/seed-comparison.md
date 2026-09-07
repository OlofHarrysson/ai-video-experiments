# Same model, fixed versus changing seed

2026-09-07. Authorized: two matched short feedback sequences, identical opening seed and artwork. A holds seed 7301 throughout; B uses 7301 for the opening, then 7302, 7303, etc. Seed numbers select noise, not a smooth interpolation.

## Question and controls

Can this model recipe preserve and gradually evolve its own opening? How does changing only the diffusion seed policy affect that behavior?

Generate the opening with SDXL base 1.0 and `xl_more_art-full_v1` LoRA at 1.1, including CLIP strength. Use the exact same model/encoders/VAE/LoRA, constant portal prompt, negative prompt, 1024×576 resolution, DPM++ 2M/Karras, 18 steps and CFG 4.5 throughout. Opening uses denoise 1.0 from empty latent; feedback uses 0.58 on the previous image. Both branches share the same saved opening pixels.

Use installed Difforum feedback/camera nodes. Small 2D zoom 1.002 per update; no rotation/translation, guide-flow injection, depth, ControlNet, prompt travel, extra pixel noise, sharpening, colour correction or RIFE. This isolates seed policy in a minimal same-model loop. The camera is an ordinary zoom for this diagnostic, not the earlier ring-derived flow or the future 3D test. Same-model production removes a confound, but does not prove it caused the earlier marsh failure: the composition also differs.

## Execution and review

1. Generate and inspect one fresh opening.
2. Generate the first four frames of both branches, inspect the first repaint and gradual changes.
3. Continue each branch from its own frame 3 through frame 47. Both reload an 8-bit PNG at that checkpoint; preserve the first four frames and check the join. Absolute frame indexing keeps B's seed advancing correctly. Later differences include accumulated feedback divergence; frame 1 provides the direct matched-input seed comparison.
4. Produce two six-second clips at 8 generated FPS, packaged at 24 FPS by repeating frames. Review an evenly spaced overview, consecutive first frames and the checkpoint join. Present both playable clips with plain-language findings.

`seed_comparison.py` uses the existing serverless transport and immutable local archives. Paired cloud batches concatenate A then B for transport; split them before presenting. Do not submit an uncertain job again: use the shared collector and inspect its receipt.

## Results

Completed. [A: fixed seed](../exports/seed-v001/fixed/continue.mp4) and [B: changing seed](../exports/seed-v001/increment/continue.mp4) each contain 48 source frames / six seconds. Both begin with the exact same opening pixels. These are raw feedback results without interpolated frames; 24 FPS delivery repeats each 8 FPS source frame three times.

Assistant first-pass preference: **B, changing seed**, for further creative work. User playback judgment is pending.

| Part of shot | A: fixed seed 7301 | B: seeds 7301–7348 |
| --- | --- | --- |
| First repaint, 0.125 s | Immediately increases contour weight and adds dense bright dots and lines. Scene layout remains recognizable, but the look changes substantially. | Retains more of the opening's softer shading and broad layout; local details still change. |
| First second | Outlines, white spots and orange/teal regions become strongly graphic and dense. | Central flame becomes an oval light within an emerging shell. Portal and person remain recognizable. |
| 1.25–2.625 s | Similar dense composition across the overview samples. | Consecutive source-frame samples show a mask/head-like object developing around the light, including side shapes and hanging appendages. Some contour/figure changes remain noticeable. |
| Later samples, through 5.875 s | Pattern largely settles, with comparatively little semantic progression. It is not pixel-identical across frames. | Floating head-like form becomes larger and gains detail while portal/person context persists. The artwork evolves rather than remaining identical. |

The seed policy clearly matters in this run. Fixing the numerical seed did **not** preserve the initial appearance better. Repeated noise may reinforce a particular pattern, but that explanation remains a hypothesis; this comparison does not isolate the internal mechanism. Only one opening seed, prompt and model recipe were tested. Later branch differences include accumulated input-image differences. The first repaint is the cleanest direct seed comparison because its two inputs match.

Both branches use the same model throughout, yet A still undergoes a pronounced appearance change. Therefore same-model provenance is a useful control, not a sufficient guarantee of gradual evolution. This experiment also does not establish that cross-model input caused the earlier marsh failure. Keep P3 + RIFE as a creative comparison, not an otherwise matched control. Recommended next creative test, subject to Olof's playback preference: carry B's recipe into a small intentional 3D move with a nearby foreground layer.

## Review and validation evidence

- [Opening](../exports/seed-v001/opening.png), [first four source frames](../exports/seed-v001/first-four.jpg).
- Shared review harness: [paired six-point overview](../exports/seed-v001/reviews/v001/contact-sheet.jpg), [first twelve source-frame positions, page 1](../exports/seed-v001/reviews/v002/contact-sheet.jpg) and [page 2](../exports/seed-v001/reviews/v002/contact-sheet-002.jpg), [B's shape emergence](../exports/seed-v001/reviews/v003/contact-sheet.jpg). All four review sheets and the opening/preflight sheet were visually inspected. Review labels count decoded **24 FPS video frames**; divide by three for source-frame indices. The source sequence is 8 FPS.
- Review establishes sampled visual progression and adjacent-frame differences; it is not a substitute for the user's normal-speed playback judgment. The four-frame checkpoint boundary is covered by consecutive-frame inspection. The loaded boundary images matched their preserved PNG pixels exactly.
- Local graph checks confirm common model/conditioning nodes and otherwise equal feedback settings; only seed mode and the corresponding branch input differ. Pixel checks establish identical openings and unchanged continuation anchors. Both exports have 48 source PNGs and 144 delivery frames at 1024×576, exactly six seconds. [Validation](../exports/seed-v001/validation.json).
- Same worker handled all three jobs: ComfyUI 0.34.0, Python 3.12.3, PyTorch 2.11.0+cu128, RTX 4090; reused image `f106834b7`, digest `sha256:e273da07af0fd230849c22654477de5123ad6e284129c1d022f5230ae4ee03f2`. Model pins/checksums remain in the [Dockerfile](../../../serverless/Dockerfile); actual runtime and executed workflows are archived with each run.

| Run | Queue/startup delay | Execution | Output |
| --- | ---: | ---: | --- |
| `20260907T181815017430Z-seed-opening-1f` | 203.886 s | 8.244 s | One shared opening |
| `20260907T182159936451Z-seed-preview-paired-8f` | 0.103 s | 11.092 s | First four frames of each branch |
| `20260907T182244104649Z-seed-continue-paired-90f` | 0.120 s | 148.764 s | Two frame-3-through-47 continuations |

Two earlier submissions were explicitly rejected with HTTP 409 `ENDPOINT_PAUSED` despite the control plane reporting max workers 1; neither returned a job ID and the queue remained empty. The rejection receipts are preserved. A previously triggered GitHub build also updated the endpoint image during setup; the verified image was restored, and all accepted jobs used the same worker. These are setup observations, not diffusion failures. No build or new node package was needed for this experiment.

All 113 cloud objects (93,452,955 bytes), including inputs, workflows, diagnostics and manifests, were downloaded and verified byte-for-byte. The endpoint is paused with min/max workers zero and the temporary volume was detached/deleted. Final worker, Pod and volume inventories are checked separately in the private session receipts. Observed account balance decreased from $47.3965197502 to $47.3383073521, approximately **$0.0582**; current spend rate is zero. This is an observed account delta, not an itemized invoice. Session receipts: `apps/deforum/work/seed-comparison-session/`.

## Reuse

From `apps/deforum/`, run `uv run --env-file .env --with pillow python projects/motion-guide-study/experiments/seed_comparison.py STAGE`. Stages are `opening`, `preview`, `continue`; `check` validates the paired graph and `review` regenerates versioned overview/early-frame reviews. Existing generations are immutable. Use a new export version before a new experiment; never rerun an uncertain submission. The shared collector can retrieve an accepted interrupted job, after which export assembly must be reconciled from its preserved run receipt. The current cloud volume has been deleted after local verification and cannot be reused.
