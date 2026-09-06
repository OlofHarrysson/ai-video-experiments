# E01 — Invitation → signal → reveal

## Before rendering

Question: can three short shots tell a legible story without dialogue, while preserving a preferred image style better than one long morphing shot?

1. Invitation: lantern foreground, boardwalk leading to the distant observatory; push forward.
2. Signal: a closer view along the same boardwalk; a bright amber trail leads to the observatory.
3. Reveal: arrive at the observatory, now opened onto an impossible luminous garden and sky.

Create two new story keyframes with Seedream 4 Edit, using the preferred original as the image reference. Animate each with SDXL base, Difforum feedback, 32 frames at 8 generated FPS, a 1.015 zoom per step, no rotation, denoise 0.24, CFG 5, 24 steps, incrementing seed, noise 0 and sharpening 0. The three-shot edit is one experiment. All shots are 2D pushes; this tests staging/editing rather than claiming solved 3D geometry.

Hypothesis: explicit new keyframes and cuts will make a stronger narrative change than relying on a prompt schedule to invent all the action. Low denoise should retain the Seedream look better, although softness or lost detail may remain.

Review: inspect the actual encoded cut at shot starts, middles, ends and either side of each cut. Check attention target, state change, framing, drift and abruptness. Frame samples cannot establish smooth playback or measure flicker reliably; preserve the playable video for Olof.

Budget ceiling $8 for this experiment, within the authorized session. Public endpoint reference: [RunPod Seedream 4 Edit](https://docs.runpod.io/public-endpoints/models/seedream-4-edit), read 2026-09-07. Its documented inputs are prompt, image URLs, size and safety checker; listed price $0.027 per image. Actual receipts govern cost. Model revision is managed by the provider and not exposed.

## Results

### Story keyframes

Two Seedream Edit calls completed. Both used the preferred original's existing HTTPS URL in `images`; data URLs were not tested. The response image field is `output.result`, rather than the `output.image_url` shown in the documentation. Both outputs were 2560×1440 despite requesting `2048*1152`, then resized with Lanczos to 1280×720 for ComfyUI. Each receipt reports $0.027, $0.054 combined.

The inspected signal keyframe keeps the brushwork and palette, enlarges the observatory and adds a clearly legible amber trail and doorway. The reveal keyframe depicts the same architectural motif split open around a golden portal with floating islands and waterfalls. Both establish the intended story state as stills.

Exact reproducible inputs and receipts are preserved under `references/assets/signal/` and `references/assets/reveal/`. The project recipe's `review` action calls the shared `video_review.py` harness with explicit shot-boundary events at 4 and 8 seconds and samples before and after each event.

### Animation review

Opening and signal clips were decoded through the local harness at approximately 0, 1.96 and 3.96 seconds. The camera push is clearly visible. Low denoise, zero added noise and zero sharpening do not preserve the source texture: both clips lose fine painted detail by the middle and become noticeably soft by the end. The signal path remains readable, but the dome, reeds and mushrooms simplify. These settings should not become the default recipe for preserving Seedream's look. Several controls differ from the previous session, so this test does not isolate the cause to denoise alone.

The visual story depends on the cut from one staged state to the next. There is no generated continuous signal travelling down the path, no continuous dome-opening action, and no verified 3D camera move. This is an editing and keyframe experiment with per-frame SDXL repainting.

### Shorter practice cut

After inspecting the full render, `e01-v002` selects invitation frames [0,12), signal [0,12) and reveal [0,16): 1.5 + 1.5 + 2 seconds. This five-second cut uses earlier, clearer portions of the same runs and adds no inference. The twelve-second version and every source frame remain intact. Its cut manifest records exact source hashes.

[Shorter video](../exports/e01-v002/preview.mp4) · [Source ranges](../cuts/e01-v002.md) · [Timed review](../exports/e01-v002/reviews/preview/v001/contact-sheet.jpg).

Eleven decoded samples include the new cuts at 1.5 and 3 seconds and their adjacent frames. The shorter selection avoids the most degraded endings while retaining all three story states; softness still develops within each shot. This demonstrates choosing usable source ranges after review, not fixing the animation model. Playback rhythm remains for Olof to judge.

### Final cut and verdict

[Play E01: invitation → signal → reveal](../exports/e01-v001/preview.mp4) · [timed-frame contact sheet](../exports/e01-v001/reviews/preview/v001/contact-sheet.jpg) · [versioned cut](../cuts/e01-v001.md).

The final 12-second cut has three four-second shots. I inspected 11 frames decoded from the encoded video: 0, 2, 3.875, 4, 4.125, 6, 7.875, 8, 8.125, 10 and 11.875 seconds. The before/after cut samples establish a distinct sharpness reset at both new keyframes. The reveal retains its portal silhouette and warm/cool contrast, but its floating islands and waterfall detail also dissolve as the push progresses. This review supports claims about composition, state change and detail drift; it does not establish a playback flicker rating.

- Useful result: Seedream edits preserve enough palette and architecture to create clear consecutive story states. Shot changes and enlargement of the observatory direct attention toward a visible payoff.
- Failed hypothesis: this low-denoise, no-noise, no-sharpening SDXL recipe does not preserve the preferred texture. The increasing softness is severe enough that this is a learning cut, not a finished-quality movie.
- Next lesson to carry forward: keep explicit keyframes and versioned assembly; improve detail retention before lengthening these shots. Compare animation configurations separately so the cause can be isolated.

### Execution and verification

| Shot | Run | Queue / execution seconds |
| --- | --- | --- |
| Invitation | `20260906T231837804686Z-story-32f` | 80.153 / 101.651 |
| Signal | `20260906T231949672077Z-story-32f` | 11.389 / 104.198 |
| Reveal | `20260906T231950862204Z-story-32f` | 85.256 / 97.719 |

All three custom jobs completed and were collected, with no retries or resubmissions. Each first frame is pixel-identical to its prepared keyframe. The immutable assembly contains 96 source frames; ffprobe verifies 1280×720, 12.000 seconds, 288 delivery frames at 24 FPS. Frames are repeated from 8 generated FPS, without optical flow or interpolation. `exports/e01-v001/verification.json` preserves terminal status, timings and checks; each run preserves its executed graph and remote archive. Shared worker/model pins are documented in the app runbook, with runtime receipts retained in each run.

Public Seedream edits reported $0.054 combined. Custom GPU execution totaled 303.568 seconds across overlapping jobs; this is not an itemized billed-cost figure and excludes provisioning/idle accounting. Parent session owns the shared endpoint and archive volume, including final cloud-copy verification and cleanup. E01 made no infrastructure changes and has no pending jobs.

### Local recipe

From `apps/deforum`, use `uv run --env-file .env --with pillow python projects/marsh-story/experiments/story.py ACTION`. The completed actions were `prepare`, `keyframe signal`, `keyframe reveal`, `render invitation`, `render signal`, `render reveal`, `assemble`, and `review`. Creation/assembly refuse existing target folders; do not repeat render actions to recover a job. Use the shared `experiment.py collect` command with an existing run, or `collect-keyframe SHOT` for an existing public job. `review` creates a new immutable sample version through the shared harness.
