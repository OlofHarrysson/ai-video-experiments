# Two sampler alternatives for the three-second twist

2026-09-08. Completed comparison. Grounded in the [model and sampler research](../../../../../docs/research/model-sampler-recipes.md).

Compare the accepted SDXL base + more-art v1 recipe (`dpmpp_2m`) with `euler` and `euler_ancestral`. The current art LoRA gallery includes both Euler variants, but references older LoRA weights and high-resolution finishing; these are candidates, not exact reproductions. Ordinary SDXL does not have the fixed low-step constraints of Lightning models.

Keep Karras scheduling, 18 sampling steps, CFG 4.5, denoise 0.45, LoRA strength 1.1, opening image, prompt, incrementing seeds, three-second twist and cadence 3 matched. No extra pixel noise, mask, RIFE or depth. Hold LoRA strength despite the creator's 0.8–1.0 recommendation to isolate the sampler; consider its strength separately later. This tests sampler behavior at our established operating point, not each sampler's best possible configuration.

Reuse the archived DPM++ 2M baseline after a fresh first-anchor pixel-equality check. Each alternative produces 12 new generated anchors. Every next input comes from that branch's previous generated anchor, warped to its new position. Cadence intermediates warp both generated endpoints to the display time and blend them, as in the accepted previous experiment. The terminal anchor supports the last intermediate frames.

Review an evenly spaced overview, a consecutive-frame window and matched full-size crops. Look for repaint jumps, grain, meaningful morphing, astronaut continuity and motion visibility. Do not rank temporal quality from sharpness alone. Same numeric seeds align the input schedule; different samplers need not consume the same internal random sequence. Report observed runtime as well as steps.

## Results

Both new variants completed. Each has 13 anchors including the shared opening and terminal support frame, 36 cadence frames and a three-second 24 FPS export. The old baseline is preserved alongside them.

- [Baseline versus Euler](../exports/samplers-v001/baseline-vs-euler.mp4): baseline left, Euler right.
- [Euler versus Euler ancestral](../exports/samplers-v001/euler-vs-ancestral.mp4): Euler left, ancestral right.
- Full-size individual clips: [baseline](../exports/samplers-v001/baseline/cadence/preview.mp4), [Euler](../exports/samplers-v001/euler/cadence/preview.mp4), [ancestral](../exports/samplers-v001/ancestral/cadence/preview.mp4).

**Assistant recommendation: retain DPM++ 2M as the control; keep Euler ancestral as a meaningful expressive alternative.** Ordinary Euler has a similar broad progression to the baseline, with different flame and portal contours. Ancestral diverges more: the portal becomes a stronger orange/red, its cavities and cyan outlines change, the flame develops a dark oval and speckled texture, and the astronaut acquires different helmet/torso details. At anchor 33 both Euler variants introduce an orange spherical form at the lower-left edge. Neither demonstrates solved subject consistency.

Five evenly spaced decoded timestamps compare Euler/ancestral across the clip. A seven-frame window from 2.25 to 2.50 seconds shows the paired cadence intermediates and next anchor; no abrupt whole-scene replacement is apparent in this sampled window. Both still redraw details. Full-size anchor 33 confirms extra fine speckling on ancestral's flame/portal. That is not evidence of the same grain mechanism as our earlier pixel-noise injection. The earlier all-variant overview also compares anchors 0, 15 and 33. These are sampled-frame findings; Olof's playback preference is pending. A different prompt, LoRA strength or denoise may change the ranking.

Review artifacts: `../exports/samplers-v001/overview.jpg`, `reviews/overview/v001/`, `reviews/transition/v001/`, and the full-size anchor folders. [review_samplers.py](review_samplers.py) verifies isolation/provenance and builds labeled comparisons. The standard `video_review.py` extracts decoded overview and consecutive-frame pages.

## Execution and validation

All **25 accepted jobs completed**: 24 new anchors and one fresh baseline probe. The probe was pixel-identical to the archived first baseline anchor. Graphs differ only in sampler name and output prefix; the two first warped inputs are byte-identical. Every anchor hash and displayed anchor identity is checked. All five videos fully decode with 72 frames at 24 FPS and duration 3.0 seconds.

All jobs served on RTX 4090 worker `pw7ue7wbxpgl4b`, image `2d7cda891`, ComfyUI 0.34.0, PyTorch 2.11.0+cu128 and Python 3.12.3. Median reported execution was **4.141 seconds for Euler** and **4.309 seconds for ancestral**; all jobs together reported 116.893 seconds, including the 12.738-second reference probe. These are per-job execution times, not full local round trips or identical neural-network evaluation counts. The first probe spent 121.557 seconds in queue.

During startup, the connected Hub changed the endpoint's desired image to the prior commit's `06592ba42` build. Additional workers attempted to initialize that image, but every completed job used the older worker/image above. The first-anchor equivalence check passed. This illustrates why desired endpoint configuration alone is insufficient provenance. No model or workflow rebuild was needed for the sampler changes.

All **150 cloud objects, 45,274,085 bytes**, were verified byte-for-byte against local copies. Endpoint min/max workers are zero; worker and volume inventories are empty. The owned 10 GB US-IL-1 volume `nbkm683fub` was detached and deleted after verification. Private status/copy receipts and the closed deployment file remain in ignored `work/sampler-session/`.

Observed account balance decreased by $0.023 to $45.743; reported current spend rate is zero. This is a session balance observation, not a finalized inference-only bill.
