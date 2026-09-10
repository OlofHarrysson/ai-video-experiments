# Three-step repainting: starting-noise sweep

## Plan recorded before rendering

Olof approves the diffusion test and requests several noise levels. Compare the preserved 0.6545668244 baseline against 0.62, 0.60 and 0.56. Each new six-second branch contains five recurrent repaints from the exact accepted opening at absolute second three. Three native sampling intervals remain, with only the starting sigma changed by core SetFirstSigma; later sigmas stay 0.5128440857, 0.3109010756 and 0. These modified first intervals are experimental, not an official Krea recipe or a percentage of visible pixels repainted.

Keep Krea Turbo FP8, text, Euler, CFG1, shift1.15, incrementing seed sequence, Lanczos4/reflected borders, time-based twist/expansion, one-second repaint interval and 24fps. The previous generated anchor is warped and initializes the next repaint; no independent redraws or reference conditioning. Reuse the existing full-scale RIFE 4.25 settings for all variants. Preserve raw diagnostics and the native warp-only final second of each branch.

One short-lived Pod reuses the retained EU model/runtime volume. Live catalog has an RTX PRO 4500 at $0.72/hour; the historical control used RTX5090. Render a fresh five-repaint control on the same GPU as all three variants to avoid confounding hardware/runtime differences with sigma. Preserve the historical control too. Total: twenty new repaint calls.

Inspect every generated anchor and selected corresponding warped inputs, plus overview/interpolation windows. Judge retained shading, detail, spatial motion and structural evolution separately from repaint change. Lower pixel difference alone can reflect blur. Deliver a small shortlist with all four versions indexed, preserving every generation and receipt. Download/hash-check results before deleting owned compute; retain the authorized model volume.

## Results

All four six-second clips are complete at 1536×1024, 24 fps. This is an assistant frame-based first-pass review; Olof has not selected a noise level. The 0.655 control remains the accepted baseline pending playback feedback.

| Starting sigma | Assistant observation | Mean repaint change, RGB /255 |
| --- | --- | ---: |
| 0.655, native control | More newly articulated spires, holes and architectural detail; larger redraws. | 15.96 |
| 0.62 | Modest reduction, retaining elaborate filigree; visually close to the control. | 14.62 |
| 0.60 | Candidate compromise: smaller redraws and readable arches, with some loss of fine ornament. | 13.91 |
| 0.56 | Smallest redraws, but broader, simpler surfaces and less intricate rebuilding. | 12.11 |

The metric is the mean absolute RGB difference between each warped initialization and its repaint, averaged over five calls. It measures redraw magnitude, not flicker, sharpness or beauty. Each branch becomes its own recurrent trajectory after the first repaint; these are not twenty repaints of an identical input. The same starting image and seed sequence control the comparison. The trend supports the noise-control hypothesis in this shot, but does not establish an optimum across artworks or long sequences.

Start with **control versus 0.60**. Watch the cream arch on the left and the small structures inside it. The lower-noise version rebuilds them less aggressively; the control develops more small spires. The gold central object remains recognizable in every branch. Lowering noise also reduces some of the detail we liked in three-step sampling, so 0.56 is a useful boundary test rather than my proposed default.

- [Main comparison: control left, 0.60 right](../exports/starting-noise-v001/shortlist/preview.mp4).
- [All four](../exports/starting-noise-v001/all-four/preview.mp4): top left control, top right 0.62, bottom left 0.60, bottom right 0.56.
- Individual finished clips: [control](../exports/starting-noise-v001/sigma-control/cadence-24/interpolated/preview.mp4), [0.62](../exports/starting-noise-v001/sigma-062/cadence-24/interpolated/preview.mp4), [0.60](../exports/starting-noise-v001/sigma-060/cadence-24/interpolated/preview.mp4), [0.56](../exports/starting-noise-v001/sigma-056/cadence-24/interpolated/preview.mp4).
- Each branch preserves its raw `preview.mp4`, every painting, warped initialization, executed workflow, `verification.json`, RIFE receipts and final frame manifest beside these outputs.

## Implementation and verification

[Generation](starting_noise.py) adds core `SetFirstSigma` to the existing sampler graph. The later sigmas are unchanged; lowering the first sigma also shortens the first sampling interval. This is a schedule modification, not an independently varied RGB-noise overlay. Requested and executed graphs agree for all twenty calls. [Review and assembly](starting_noise_review.py) verify previous-output → spatial warp → sampler initialization → new-output hashes and every repaint warp, then reconstruct raw diagnostics locally.

The runner's new `graph_factory` and `build_frames` options preserve its defaults. After the control, raw diagnostic reconstruction moved to the Mac to avoid holding paid GPU time for CPU frame assembly. The five recurrent repaint warps still execute before their corresponding diffusion calls. Control raw frames were generated remotely; locally reconstructed variant frames use the same time-based mapping and Lanczos function. Original and final executed source snapshots are archived.

RIFE 4.25, scale 1.0, weights/code hashes and all finishing settings match the previous baseline. First-pair midpoints were visually inspected before full interpolation. All six painting timestamps are pixel-identical to generated anchors. Frames 0–119 use RIFE between paintings; frames 120–143 use native warp-only motion after the final painting. Nothing from interpolation feeds back into generation. All four finished videos pass full decoding and 144-frame/24-fps/six-second checks. Twelve existing timing/interpolation tests pass; a graph comparison confirms only the planned first-sigma override differs from the native recipe.

Visual inspection covers every painting in four six-image contact sheets, full-size final paintings for control/0.60, first-pair midpoints, and a timestamp-matched overview plus consecutive-frame transition window. Some softened/doubled fine detail remains in interpolation. These sampled-frame observations do not replace human playback judgment.

## Execution and resource receipt

- GPU: one RTX PRO 4500 Blackwell Pod at $0.72/hour, reusing the retained EU-RO-1 model/runtime volume. A fresh control avoids comparing new variants only against the historical RTX5090 run.
- Runtime: ComfyUI commit `12d5279438bfefc058a269eae805ceab6047777f`, PyTorch `2.10.0+cu128`; three cached Krea files verified without downloading models.
- First graph: 141.95 seconds including model setup; subsequent graphs about five seconds. The full remote batch took 509.46 seconds including spatial work and the control's raw assembly. RIFE pair inference ran locally at roughly six seconds per pair, excluding file handling/encoding.
- Local archive verification: **490 files**, archive SHA256 `f9551840d50f838a8192073d32793edb750e70d0ed95194bc3e7802dda0394a1`. All twenty generated results and their remote input/output images are preserved. Private receipts live in `apps/deforum/work/starting-noise-session/`.
- Owned Pod deleted after download/hash verification. Live post-cleanup listing contains no Pods. The authorized 50 GB `deforum-models` volume remains; its storage charge continues as previously agreed.
- Setup repair: extraction needed `tar --no-same-owner` on the network volume. The failed ownership restoration happened before inference; central friction record `AF-20260910-115109` captures it.

