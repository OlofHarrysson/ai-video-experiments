# Ease motion while repainting continues

## Accepted test

Olof likes strong motion early but rejects the excessive late deformation. Large recognizable forms should persist until a deliberate transformation is wanted, rather than remain permanently fixed. Prompt changes are a future means of directing those transitions; negative prompting is model/guidance-dependent, not guaranteed object removal.

Preserve the existing stronger-motion shot through the saved painting at six seconds. Compare two six-second continuations: unchanged continuous twist/expansion, and the same motion smoothly decelerating during 6–8s, with no further spatial movement during 8–12s. Diffusion still runs once per second through 11s; the final 11–12s interval retains native warp-only behavior (a hold for the eased branch). Both deliveries are twelve seconds at 24 fps with identical preserved openings.

Keep the original Oracle prompt, Krea weights, incrementing seeds, Euler/CFG1, sigma schedule `[0.6, 0.5128440857, 0.3109010756, 0]`, Lanczos and RIFE 4.25 scale 1. No prompt, model, reference-conditioning or mask change. Render both endings on the same runtime: ten fresh jobs total, five per ending. This avoids attributing cross-runtime differences to motion.

## Motion definition

The original spatial mapping is evaluated at an effective motion time. Effective time equals shot time until 6s. With `u=(t-6)/2` during 6–8s, effective time is `6 + 2*(u-u^3+0.5*u^4)`. It remains at 7s thereafter. Its speed falls smoothly from one to zero, with no reset to the original undeformed image. Equal effective start/end times return the image unchanged rather than performing an unnecessary remap.

The preserved opening and all source paintings remain immutable. New runs, receipts, raw diagnosis, motion-only preview, final videos and comparison belong in `exports/eased-motion-v001/`. Main owns the temporary Pod, verified downloads and deletion; retain the authorized EU model volume.

## Question

Does easing sustained deformation preserve the attractive composition while repainting continues? If held paintings still deteriorate, recurrent repaint drift remains a candidate. A successful hold would support bounded motion phrases; it would not establish a universal cure or test deliberate prompt-driven object replacement.

## Results

Execution completed on the retained EU model/runtime volume with an RTX PRO 4500 at $0.72/hour. All three Krea files were hash-verified with no downloads, and ComfyUI remains 0.34.0 / Torch 2.10.0+cu128. An initial local runner error (missing run directory) occurred before any inference; the failed initialization was preserved, the directory creation was fixed, and a fresh immutable receipt started.

The motion-only preview, starting from the saved six-second painting, already reproduces the face leaving the frame and the collar expanding in the continuous branch. The eased branch retains its framing. This is direct evidence that continued spatial deformation contributes to the late composition failure independently of repainting. The painting findings below show the same framing difference with recurrent diffusion.


**Prompt-conditioning verification:** the archived graph uses `SamplerCustom` with CFG 1 and a `ConditioningZeroOut` negative input. Live pinned `comfy/samplers.py` skips unconditional/negative conditioning when CFG equals 1 unless the optimization is explicitly disabled. Merely inserting negative text would not provide removal guidance here; positive prompt changes and any separate guidance experiment must be distinguished. No guidance change is made in this test.


## Painting findings

An independent subagent reviewed all six painting timestamps from 6–11s in both branches, with selected native images. Main also inspected both final 1536×1024 paintings. The eased ending keeps the tilted face, circular architecture and gold form in frame, with clear shading and recessed surfaces. Continuous motion pushes the face to the upper edge and expands the collar into most of the image.

Diffusion still changes the held scene: the gold form develops architectural patterns, the eyes and eyebrows change, and surrounding cutouts are reinterpreted. Easing improves composition retention in this sequence; it does not freeze the picture or establish indefinite repaint stability. The assistant's painting-level recommendation is the eased branch. Whether the held passage is engaging is a separate playback question.

## Execution and resource receipts

Ten fresh repaints and 234 archived files were downloaded and SHA256-verified. Archive digest: `d82977784c997786a0a50d11569feaab73eaf267a0456d602cb75f6e81f218f7`. Seven source paintings per branch were preserved, including the common six-second starting point. All generations and failed pre-inference initialization records are local. The first graph took 85.994s including model loading; the remaining nine took 5.157–5.240s each. These are graph timings, not end-to-end turnaround or billing totals.

Owned Pod `sn7gne6h6com1n` was deleted after verifying downloads and an empty queue; the subsequent Pod listing was empty. The 20 owned ComfyUI input/output files and `/workspace/eased-motion-session` scratch folder were removed after local verification. The authorized 50 GB EU model volume, cached weights and runtime remain intact. Private receipts are in app-level `work/eased-motion-session/`.

## Artifacts and reproduction

- [Twelve-second comparison](../exports/eased-motion-v001/comparison/preview.mp4): continuous left, eased right.
- [Eased version](../exports/eased-motion-v001/ease/cadence-24/interpolated/preview.mp4).
- [Fresh continuous control](../exports/eased-motion-v001/continuous/cadence-24/interpolated/preview.mp4).
- [Motion-only comparison from six seconds](../exports/eased-motion-v001/motion-only/preview.mp4).
- Raw videos, anchor PNGs and feedback receipts remain beside each final.

Run from `apps/deforum/`. `eased_motion.py --deployment PATH` generates both five-repaint endings using the existing explicit Pod transport. The [review helper](eased_motion_review.py) supports `check`, `preview`, `build-raw`, `prepare`, `finish` and `compare`; optionally pass `--case continuous` or `--case ease`. Between prepare and finish, use the unchanged local `interpolate.py` on twelve `rife-sources` at source FPS 1, multiplier 24, with the normal inspected pair gate. Final verification checks all graph/seed/feedback inputs, all preserved paintings, held decoded RGB inputs, exact original opening frames 0–144, and the final native hold.


**Interpretation:** stopping deformation does not reduce the configured repaint noise or stop local redrawing. Mean absolute input-to-repaint changes at 9–11s remain about 16 RGB levels in both cases; this diagnostic is not a semantic or temporal-quality score. The clearer benefit is retaining the composition. A future intentional subject transition can branch from the saved eased 8s painting, preserving this framing while changing the positive scene prompt; that follow-up is not part of this run.


## Finished-video review and validation

Both individual finishes are 1536×1024, 288 frames at 24 fps, twelve seconds, with RIFE 4.25 scale 1 unchanged. The comparison is 1536×554 with the same timing. All three videos fully decode. Original opening frames 0–144 are pixel-identical in both deliveries; every diffusion anchor is preserved. The eased 11–12s tail is an exact native hold because no later repaint exists and spatial movement has stopped. `delivery-verification.json` and per-branch continuation receipts record these checks.

Main inspected six evenly spaced finished comparison samples and every frame in a 9.42–9.58s window, alongside the native final paintings. The eased face and enclosing rings stay readable; the continuous ending becomes dominated by the collar and cropped face. Local details still morph in the eased version, including block-like patterns inside the gold form. This supports easing for this shot's framing problem, without establishing complete temporal stability or intentional control over every transformation. The stationary ending may need a new action or prompt transition for a longer film. Assistant recommends the eased branch; Olof's playback verdict is pending.

The held-input validator compares decoded RGB, because ComfyUI's PNG metadata changes file hashes even when no pixels change. An independent agent caught this before final preparation; all held-input pixel checks passed. Shared production helpers and prior outputs were unchanged.
