# Shape-controlled watermelon: results

2026-09-27. **A plain rendered circle is enough for useful spatial control with several current image editors. For the next motion experiment, use GPT Image 2.5 Sunburst with the circle guide plus a fixed reference watermelon.** This is a screened assistant recommendation; Olof has not yet judged these results.

We generated 53 outputs across five models, going from a broad still-image comparison to position/size tests and a seven-position motion comparison. Paid execution used Fal and an owned temporary RunPod A100. No Deforum production recipe was changed.

## View the result

- [Four-panel motion comparison](../../../remotion/projects/watermelon-guides/renders/v001/comparison.mp4): guide; independent Sunburst; Sunburst with reference; Qwen masked generation. Seven generated frames held at **2 fps**, delivered as a 3.5-second, 24 fps video. No interpolation. Watch the rind stripes, especially when moving through the middle positions.
- [Smooth SVG-only guide](../../../remotion/projects/watermelon-guides/renders/v001/guide-motion.mp4).
- [All initial candidates](exports/round1/comparison.jpg), [position/size and seed tests](exports/round2/comparison.jpg), [motion frames](exports/round3/comparison.jpg).

![Motion-aligned rind crops: independent, fixed reference, masked generation](exports/round3/aligned-texture.jpg)

The fixed reference clearly reduces changes in the broad stripe pattern. Small stripe boundaries, highlights and apparent orientation still vary, especially near the first two transitions. It is not pixel-identical translation. Independent generation and the fixed-seed open model visibly redraw the fruit more.

## Breadth and generalization

The first test used a 360-pixel-diameter circle centred at (256,512) on a 1024-square canvas. Further tests moved it to (768,512), then shrank it to diameter 200 at (720,320). A passing result must contain one realistic watermelon in the requested region, with approximately the requested silhouette. Plausible fruit elsewhere in the image is a failure.

| Method | Observed result | Approximate geometry |
|---|---|---|
| GPT Image 2.5 Sunburst, coloured guide | Passed left, right and small; passed all seven Remotion positions | First three: centre error under 1 px, diameter within 1% |
| Seedream 5 Pro, coloured guide | Passed all three positions/sizes | Centre error under 2 px, diameter within 2% |
| Nano Banana Pro, coloured guide | Passed all three positions/sizes | Centre error under 3 px, diameter within 1% |
| Qwen Image 3, coloured guide | Passed left/right; small fruit became large and centred | Small case: centre error about 266 px; diameter over 3× target |
| Qwen Image 2.1 Union, inpainting mask | Kept placement in three layouts at two seeds, then seven motion positions; second seed sometimes made a flatter oval | Centre errors about 0.4–4.4 px; fruit often 1–5.5% smaller than mask |
| Qwen Image 2.1 Union, outline/depth | Public demo's left samples passed. Own runtime's outline tests and small depth tests failed, often adding a large extra fruit. Right depth passed | Not reliable enough for this recipe |
| Sunburst, blank image + alpha edit mask | One attempt produced a large centred fruit | Failed this submitted recipe; mask interpretation was not independently established |

The public Qwen demo and our pinned runtime did **not** behave equivalently on control-only inputs. Inputs, source and weight revisions were preserved, and the local loader reported zero missing/unexpected keys, but the discrepancy was not resolved. Do not infer that the adapter universally fails, or use its public-demo success to validate our own control-only integration. Masked generation is a separately verified path.

Geometry comes from colour-based foreground estimation, largest connected component and hole filling, checked against the images. These are approximate diagnostics, not ground-truth segmentation or a general model benchmark. A stricter initial green threshold missed yellow highlights and dark rind; that diagnostic is preserved separately and is not used in the final measurements. Detailed results: [measurements.json](measurements.json).

## What the input means

**Image editing:** Remotion draws an SVG circle and renders it to PNG. Send that PNG as image 1 and explicitly ask the editor to replace the green circle with a watermelon while preserving its centre, diameter and background. No depth model or special adapter is required. For continuity, send the same selected watermelon as image 2 on every request; image 1 controls placement, image 2 controls appearance. Each request is independent; no previous-frame feedback was used.

**Masked generation:** render a same-size black-and-white PNG. For this Qwen pipeline, white means regenerate and black means retain the source. Supply a blank background plus the circular white region. This local model has an explicit inpainting path. It keeps the spatial constraint but does not ensure the same rind across frames, even with the same seed.

**Depth/outline conditioning:** a synthetic spherical depth map or white outline is supplied to a trained control branch. Its accepted input distribution, model implementation and scale matter. Our results do not justify continuing with this route before resolving the integration discrepancy.

These tests establish shape-to-image placement and a small translation sequence. They do not establish physical impact, deformation, fracture, occlusion, camera motion or a finished watermelon-smashing film. The next useful creative test would add a second distinct shape for the bat and check both objects before asking for impact.

## Continuity evidence

The three motion methods received seven target centres from x=256 to x=768, at y=512 and radius 180. Sunburst with reference stayed within roughly 3 px of the requested centre; its silhouettes overlapped the target by about 98–99%. Circle-only Sunburst also placed accurately, so the reference's benefit is primarily appearance.

After aligning crops by target position, average adjacent RGB change inside the fruit was 0.140 for independent Sunburst, 0.055 with the reference, and 0.146 for Qwen inpainting (0–1 range). The reduction agrees with visual screening. This number also responds to light and minor alignment differences; it is not a semantic identity score or evidence of stable video at higher frame rates. Only seven positions were tested.

All 53 outputs were screened via contact sheets and selected full-size images. All seven source images of each motion method were inspected in aligned crops. The comparison render was checked at the middle frame, and its frame count, dimensions and duration were decoded with ffprobe. No claim of a real-time playback taste review is made.

## Costs and cleanup

| Provider/method | New outputs | Cost basis |
|---|---:|---|
| Sunburst | 18 | Token billed; published 1024×1024 high-quality, one-input estimate $0.05268; $0.10/output working allowance |
| Seedream 5 Pro | 3 | $0.0675/output at this size: $0.2025 |
| Nano Banana Pro | 3 | $0.15/output at 1K: $0.45 |
| Qwen Image 3 | 3 | $0.04/output at 1K: $0.12 |
| Public Qwen demo | 2 | No paid API charge; anonymous quota then exhausted |
| Own Qwen runtime | 24 | A100 at $1.59/hour for about 23 minutes: approximately $0.61 compute, plus small container-storage charge |

**Working total: about $3.20, allowing $0.10 for each Sunburst output.** A calculation using Sunburst's published one-input table starts around $2.34 overall, before extra reference inputs, prompt usage and storage. Neither figure is an invoice: Fal results expose no billed usage here, and RunPod billing had not posted a record when checked. A more conservative $0.25 allowance per Sunburst image still puts the session near $5.90. No additional paid jobs remain outstanding. The authorized cap was $10.

For planning, Sunburst is roughly **5–10 cents per generated 1K frame** for this kind of request, subject to token usage; Seedream 5 Pro is about **6.75 cents** with one input at this size. Thus 100 generated frames are roughly $5–10 or $6.75 respectively, before retries. Generated frames and playback frames are different: holding or interpolating images changes the number of paid generations. This is current tested pricing, not a re-verification of the older Spider-Man project's historical bill.

The Qwen runtime's median generation took 25.4 seconds, roughly 1.1 cents of active A100 time per output at the quoted rate. Setup and idle time raised this session's average to about 2.6 cents/output. Do not compare marginal GPU time with an end-to-end API bill without accounting for that overhead.

Owned Pod `vcygvora0fzfje` was created at 18:15:23 UTC and deleted at 18:38:32 UTC. All 24 remote PNG hashes matched their remote receipts first. A subsequent live listing returned zero Pods. The previously retained shared volume was not mounted or changed. Prior Krea/author-reproduction spending is excluded from this new authorization.

## Reproduction and provenance

- [Run index](run-index.json): all 53 output hashes, generation parameters, endpoints and Fal request IDs. Exact submissions, original media bytes and verification receipts stay in ignored `runs/`; private upload/resource receipts stay in `apps/comfyui/work/spatial-control-lab/`.
- [prepare.py](prepare.py) creates the static SVG/raster guides, edge/depth maps and masks. The original circle raster used analytic supersampling. Motion guide PNGs were actually rendered by [Remotion 4.0.529](../../../remotion/projects/watermelon-guides/README.md); [prepare_motion.py](prepare_motion.py) derives masks/targets from its manifest.
- [Frozen GPU source and environment](runtime/README.md). Full BF16 Qwen weights, 40 Euler steps, CFG 1, control strength 1; seeds 43 and 21101. The seven-position sequence used seed 43 throughout.
- Public Qwen demo source revision `93f834f7b3bf4c8f5bda498deabe0255e9fe9809`. Public server internals and its resolved live model hashes were not independently verified. One client validation error and one public quota failure are preserved, not counted as outputs.
- [Sunburst endpoint and pricing](https://fal.ai/models/openai/gpt-image-2.5/sunburst/edit), [Seedream 5 Pro](https://fal.ai/models/bytedance/seedream/v5/pro/edit), [Nano Banana Pro](https://fal.ai/models/fal-ai/nano-banana-pro/edit), [Qwen Image 3](https://fal.ai/models/alibaba/qwen-image-3/edit), [Qwen 2.1 control model](https://huggingface.co/alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union). Catalog/schema/pricing checked on the experiment date.
