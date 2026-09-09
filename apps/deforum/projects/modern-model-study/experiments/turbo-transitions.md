# Ten-second transition and one/two/three Turbo intervals

Olof prefers the single final Turbo step over eight small updates. He requests a ten-second transition shot, followed by testing the final two and three steps. Retain Krea, the cathedral opening, ordinary warped-image feedback, Lanczos and cadence 3. No reference conditioning, frame blending, RIFE or depth.

## Design

First render ten seconds at 12 source fps: a localized twist builds over seconds 0–5; regional expansion builds over seconds 3–10. The completed twist persists while expansion takes over. Motion is defined independently of artwork, with smooth parameter ramps and invertible coordinate maps. A motion-only preview uses the original artwork and the same maps.

Use the single final interval of the verified eight-step simple/Euler schedule for 39 repaints. Then branch at the generated anchor at second 3, comparing the final two and three intervals over the next three seconds. Reuse seconds 3–6 from the long shot as the one-interval control. All branches share their initial image, motion, prompt, cadence and seed progression.

This compares native schedule tails, not step count at fixed noise: starting sigma is approximately 0.311 / 0.513 / 0.655 for one / two / three intervals. More intervals also means more initial noise and potentially more rebuilding. The earlier matched-noise experiment is preserved separately.

## Validation and review

Check forward/inverse mapping and interval composition, exact schedule tails, all generated parent/input/output hashes and requested/executed graphs. Confirm 120 source frames / ten seconds for the main shot and 36 / three seconds per branch. Review evenly spaced samples, the transition overlap and selected cadence boundaries. Preserve every attempt and show the main video plus a compact tail comparison in chat.

## Status

Complete: the ten-second single-step shot and two matched three-second branches are rendered, reviewed and verified. Human playback feedback is pending. All results are local and both owned Pods are deleted.

## Runtime and setup record

Pinned Krea Turbo FP8, text encoder and VAE match the previous experiment's SHA256 values. ComfyUI 0.34.0 commit `12d5279438bfefc058a269eae805ceab6047777f`, PyTorch 2.10.0+cu128 and an L40S 48 GB. New dependencies are installed in a session virtual environment inheriting the image's Torch installation. Unused workflow-template media packages are not upgraded on the successful replacement; this does not change the inference graph or model files.

The first Pod's transfer path was slow: eight-range downloads stalled, increasing to 32 ranges did not sustain the initial improvement, and 128 MiB ranges timed out after 240 seconds with roughly 64 MB received. Native Hugging Face Xet also remained slow. A US-NC-1 allocation failed due to unavailable capacity. A replacement allocated through US-TX-4/US-MO-1 transferred over 7 GB in under a minute with the original eight-range downloader. Runtime setup and model download were launched concurrently using detached subprocesses. The exact network bottleneck is unproven; changing placement solved the practical throughput problem.

The slow Pod produced no images and was deleted after saving logs and confirming its empty queue/output directory. Central records: AF-20260909-232456 and AF-20260909-233517. The replacement's first attempt stopped before submission because its fresh project lacked a `runs` directory. The runner now creates that directory; the pre-submission manifest and error logs are preserved separately, and no generated image was discarded.

Actual tail sigmas:

- One: `[0.3109010756, 0]`.
- Two: `[0.5128440857, 0.3109010756, 0]`.
- Three: `[0.6545668244, 0.5128440857, 0.3109010756, 0]`.

The `BasicScheduler` constructs the eight-step schedule; `SplitSigmas` selects its final one/two/three intervals. Each `SamplerCustom` initializes from the VAE-encoded warped previous generated image and adds the same seeded noise scaled by that tail's starting sigma. Intermediate display frames warp the preceding generated anchor. These are full feedback branches, not independent redraws or replacement frames over a pre-generated motion sequence.

## Results

**The ten-second transition works spatially, but the single-step recipe still loses too much shading over this duration.** The arches twist first, then regional expansion enlarges the flame and nearby architecture. The subject remains recognizable, while rich opening detail becomes flatter, dimmer decorative patterning.

![Ten seconds: twist into expansion, one final Turbo step](../exports/turbo-transitions-v001/tail-1/preview.mp4)

[Motion-only preview](../exports/turbo-transitions-v001/motion-only/preview.mp4) uses the original artwork with the same cumulative coordinate maps at 768×512. It does not accumulate repeated repaint/resampling loss. The generated shot is 1536×1024 and feeds each warped generated anchor into the next repaint.

**Three final intervals are the assistant's most promising creative candidate from the short comparison.** They restore deeper shadows, brighter highlights on the flame, and more elaborate architecture, with larger redraws across repaint boundaries. Two intervals add contrast and some rebuilding with less structural change. One keeps the familiar forms closest but remains flat. Human playback preferences for this round are pending; these are first-pass visual judgments, not an established flicker or long-duration ranking.

![Same three-second continuation: one, two and three final Turbo steps](../exports/turbo-transitions-v001/comparison/preview.mp4)

All three panels begin at the exact generated frame at second three of the main shot and cover seconds 3–6. The left panel reuses that section; it is not generated again. Individual [two-step](../exports/turbo-transitions-v001/tail-2/preview.mp4) and [three-step](../exports/turbo-transitions-v001/tail-3/preview.mp4) clips are preserved. No RIFE or frame blending is used. Each source frame is repeated for 24 fps delivery.

The larger tails also introduce more starting noise. Their greater rebuilding therefore cannot be attributed only to taking more steps. This result does not establish that a three-step tail will stay appealing for ten seconds; the next useful test is a longer three-step shot, with attention to abrupt redraw and retention of the chosen motion. Keep the accepted one-step recipe as a comparison, rather than treating this short visual preference as a universal replacement.

## Review, verification and archive

Reviewed eight evenly spaced samples from the ten-second video, full-resolution generated frames at seconds 5 and 9.75, four samples from the synchronized tail comparison, every delivered frame around a selected cadence boundary, and larger matched source comparisons on either side of that boundary. This establishes the visible changes but is not an exhaustive frame-by-frame playback-quality assessment.

**61 successful image requests:** 39 main-shot repaints and 11 in each additional branch. All parent/input/output and final-frame hashes, requested/executed workflows, exact schedule tails, shared branch starts and source/delivery frame counts passed verification. Selected coordinate warps and neighboring cadence frames were reconstructed locally and compared against the archived remote images. The main video has 120 source frames / 240 delivery frames; each short branch has 36 / 72. Forward/inverse maps and interval composition passed local coordinate checks before rendering. The runner creates the output directory on a fresh project.

Median observed request execution was **2.065 / 3.176 / 4.277 seconds** for one/two/three intervals. These exclude setup, transfer, local warping and cadence assembly; total request execution includes the first model load. The setup difficulties above dominated the waiting time.

The final archive preserves **124 remote input/output files**, including two bundled files, with verified hashes. Duplicate bytes use archive hardlinks; no distinct output was dropped. Archive SHA256: `58b19c85b73824499af6f944fcfebe02525c49e0550a66542d6c3b4db2e89fd1`. All 61 generations, the three videos, motion-only preview, comparison, input images and execution receipts are local under the project's `runs/`, `exports/`, `references/` and ignored session work directory.

Both owned Pods and their attached storage are deleted. The account is **not idle**: the separate, user-authorized persistent-volume trial owns an active Pod and a 50 GB network volume. Those resources were left untouched. The observed account balance moved from $41.57 to $40.80 during this session; concurrent activity means that change is not an isolated cost for this experiment. Do not report zero account-wide spend from this cleanup.

[Runner](turbo_transitions.py), [verification/comparison builder](turbo_transitions_review.py). Private setup, model and cleanup receipts: `apps/deforum/work/turbo-transition-session/`.
