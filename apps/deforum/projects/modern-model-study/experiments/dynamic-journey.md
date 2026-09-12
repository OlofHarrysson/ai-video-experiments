# A faster journey through changing scenes

Completed 2026-09-12. The [24-second film](../exports/dynamic-journey-v001/ramped/film/preview.mp4) preserves the watch-to-snail opening, then transforms the setting into a canyon city, underwater garden, cloud palaces and crystalline space landscape. The assistant selects the gradual transition-noise ramp after three short probes. Olof's playback assessment is pending.

Olof likes the preceding films, especially parasol-to-jellyfish, but wants longer, snappier films with changing environments and compositions. Similar-object transformations alone are insufficient. This experiment adds four environment prompts and overlapping bounded motion while preserving recurrent feedback. It demonstrates a world changing around the viewer; some inherited spatial structure persists.

## Outputs and selection

| Version | First transition noise | Painting review | Preserved video |
| --- | --- | --- | --- |
| Gentler | 0.72, then 0.64 | City appears at the first repaint; spiral remains as an architectural arch. | [4.5-second probe](../exports/dynamic-journey-v001/gentler/section-009/rife/preview.mp4) |
| Bolder | 0.84, then 0.64 | City appears immediately, discarding more shell layout; greater discontinuity. | [4.5-second probe](../exports/dynamic-journey-v001/bolder/section-009/rife/preview.mp4) |
| Ramped — assistant choice | 0.60 → 0.64 → 0.68 → 0.70, then 0.64 | Buildings appear around the shell, architectural cavities open, then the center becomes a city portal. | [4.5-second probe](../exports/dynamic-journey-v001/ramped/section-009/rife/preview.mp4), [24-second film](../exports/dynamic-journey-v001/ramped/film/preview.mp4) |

The probes share the opening, prompts, seeds, motion and three proportional sampling intervals. Each contains eight new paintings plus the saved opening. Their final half-second holds are probe diagnostics. Only the ramped candidate was extended, with reviews after 10s and 15s of continuation. The [10.5-second section](../exports/dynamic-journey-v001/ramped/section-021/rife/preview.mp4) and [20.5-second continuation](../exports/dynamic-journey-v001/ramped/section-041/rife/preview.mp4) remain preserved.

## What appears in the film

Times refer to the final joined video. Prompt events occur at 3.5s, 9s, 14.5s and 19.5s; visible transformations develop over subsequent paintings.

| Film time | Observed result |
| --- | --- |
| 0–3.5s | Preserved brass watch becomes a snail. |
| 3.5–9s | Buildings grow around the shell; its spiral opens into an arch and layered canyon city. The viewpoint pushes and rolls into the architecture. |
| 9–14.5s | Canyon shelves become coral, the passage becomes pale sand, and turquoise water, jellyfish and ivory columns emerge. The arch/corridor persists; a foreground pier increasingly fills the view. |
| 14.5–19.5s | A column grows into a tower. Violet clouds, gold spires and floating islands open the sky; some coral-like floral shapes remain. |
| 19.5–24s | Towers become faceted mountains; crystals, stars, green nebula, gold rivers and a ringed planet appear. Motion settles before the final half-second native hold. |

Main and [independent painting review](dynamic-journey-independent-review.md) agree that the ramp provides more readable intermediate forms than the initial strength pulses. Environment changes appear throughout the image. The sky and space sections introduce a different dominant silhouette and more distant open space.

Limitations: later surfaces become broader and more illustrative with less fine texture; inherited arches and columns constrain composition; the planet approaches the right edge near the ending. First-pair interpolation in the initial probes concentrates change near the midpoint, with soft overlap. The ramp improves that first transition but does not establish a general solution to repaint discontinuity.

## Recipe and feedback

- Krea 2 Turbo, the same verified FP8 model, Qwen3VL encoder and VAE assets as the preceding session. Three Euler intervals, CFG 1, reproducible changing seeds. No new model or custom ComfyUI node.
- Each repaint warps the previous generated RGB painting, encodes it and initializes the sampler from that latent. Prompt changes preserve this feedback. RIFE output never enters generation.
- Base sigmas: `[0.6, 0.512844085693, 0.310901075602, 0]`, scaled by `starting_noise / 0.6`. The first four repaints of each new prompt use `[0.60, 0.64, 0.68, 0.70]`, then 0.64. This is scene-specific evidence, not a global default.
- A painting every 0.5s: cadence 12 at 24 fps. Local Practical-RIFE 4.25, scale 1, produces eleven intermediate frames per pair. Every painting remains in the delivery. The final half-second holds the native painting after motion settles.
- Time-based Lanczos warps compose five bounded twist, expansion and translation phrases. Overlaps and direction changes maintain movement without indefinitely applying one deformation. No depth or guide-flow stage.
- Source: `ten-dollar-v001/clock-pulse/anchors/0084.png`, the preceding film's 3.5s painting. Old frames `[0,84)` are preserved and the shared painting occurs once at frame 84. See [cut v004](../cuts/v004.md).

Exact prompts, timing, motion and seeds: [gentler](dynamic-journey-configs/gentler.json), [bolder](dynamic-journey-configs/bolder.json), [ramped](dynamic-journey-configs/ramped.json). [Runner](dynamic_journey.py) records parent, initialization and generated-image hashes, executed graphs and receipts. [Finisher](dynamic_journey_finish.py) produces first-pair previews, sections and the verified prefix join.

## Verification and visual review

- **56 fresh Krea jobs:** eight gentler, eight bolder, forty ramped. All inputs, outputs and receipts are local; **924 archive files** passed byte-count and SHA-256 verification before GPU deletion.
- [Generation check](../exports/dynamic-journey-v001/generation-check.json): all 56 feedback-lineage and graph checks pass. Ten representative full-resolution warps recomputed locally exactly match remote initialization images.
- [Delivery check](../exports/dynamic-journey-v001/ramped/film/delivery-check.json): 1536×1024, 24 fps, 576 frames, 24s, 48 retained paintings, shared anchor at 3.5s, full error-free decode. Prefix and painting equality concern source PNGs; H.264 delivery is lossy.
- All new paintings were inspected in bounded contact sheets. First RIFE pairs were inspected; extended sections reproduced the earlier inspected first pair exactly before full finishing.
- [Middle transition samples](../exports/dynamic-journey-v001/ramped/section-021/rife/reviews/preview/v001/contact-sheet.jpg) show coherent arch/pier movement with softened, changing fine detail.
- Final review: eight evenly spaced samples plus consecutive-frame windows near 4.17–4.46s and 20.67–20.96s. [Page 1](../exports/dynamic-journey-v001/ramped/film/reviews/preview/v001/contact-sheet.jpg), [page 2](../exports/dynamic-journey-v001/ramped/film/reviews/preview/v001/contact-sheet-002.jpg), [page 3](../exports/dynamic-journey-v001/ramped/film/reviews/preview/v001/contact-sheet-003.jpg). The shell opens into architecture across the first window; later the mountain silhouette remains readable while the planet/crystal forms move and change. These samples support progression and reveal local softening; they do not replace human playback judgment.

## Runtime, cost and cleanup

The retry's cached-region PRO 6000 allocation was rejected. A fresh temporary A100 SXM 80GB in US-MD-1 started at **$1.59/hour**, using ephemeral disk. The retained EU cache stayed untouched. Verified model downloads took **85s** and runtime preparation **32s**; warm repaint round trips were roughly **8s**. Allocation-to-first-submit was about ten minutes including orchestration; it was not all model setup time. ComfyUI was pinned to `12d5279438bfefc058a269eae805ceab6047777f` (0.34.0), with runtime and asset receipts archived.

The Pod was deleted after about 31m34s. Estimated compute is **$0.8364**, plus a conservative **$0.03 disk allowance**: roughly **$0.87 for this retry**. Billing had no posted records at cleanup. The original $10 allowance also covers the preceding session's posted $0.1743 and the earlier failed startup allowance; no extra budget was needed.

An empty Pod list confirmed deletion. The authorized 50 GB `deforum-models` volume in EU-RO-1 remains; its ongoing storage charge is separate. Private budget, deployment, archive and cleanup receipts are under ignored `apps/deforum/work/dynamic-journey-session/`.

### Earlier capacity failure — 2026-09-11

The earlier allocation stayed `initializing / awaiting_container` for about fourteen minutes without usable inference. Logs were empty or timed out; later allocations were rejected. No inference ran and the owned Pod was deleted. Estimated exposure was about $0.17 compute plus disk, with billing unposted. The cause remains unverified. Local motion inversion, full-resolution warps, prefix join and final-tail checks passed before the retry. The fresh A100 establishes a working execution path, not a diagnosis of the earlier machine.

## Reproduction

Follow [the Pod runbook](../../../POD.md) and create a fresh owned deployment receipt; the saved receipt names a deleted Pod. Run `dynamic_journey.py CONFIG --deployment RECEIPT --through 4` for a probe, then advance a selected branch through 10s, 15s and the full 20.5s. Verified existing paintings resume without duplicate generation. Use a new case/output directory for changed settings to preserve attempts.

Locally run `dynamic_journey_finish.py CASE --stage prepare`, then `pair`, inspect the pair, and run `full`. The final 41-anchor section supports `join`, creating a new film directory and refusing to overwrite an existing cut. Use the app's `uv` environment with NumPy, Pillow and OpenCV; finishing calls the pinned local RIFE environment. Archive and verify remote artifacts before deleting owned compute; keep the authorized model volume.
