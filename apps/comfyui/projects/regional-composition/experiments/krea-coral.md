# Stone face and winding coral band

## Accepted final comparison

Olof approves one final regional-prompting test after preferring complete prompts for the three-robot benchmark. Test whether a drawn, curved material boundary offers useful art direction beyond a verbal description. Four images: complete prompt versus regional conditioning, seeds 21001 and 21101. No refinement, inpainting, image initialization or seed selection.

A single frontal monumental stone face fills the frame against a dark teal background. Luminous coral grows along a broad S-shaped band from forehead to chin, curving toward the viewer's right above the eyes and the viewer's left across the cheek. Both methods receive this verbal description. Only regional conditioning receives the grayscale mask; neither receives a face reference or target diagram as an image-conditioning input.

Keep the established Krea 2 Turbo FP8 assets, pinned ComfyUI 0.34.0 runtime, 1024-square canvas, eight Euler/simple steps, CFG 1 and matched initial noise. The regional graph uses built-in ConditioningSetMask with full-canvas prediction evaluation (`set_cond_area=default`). A complete-scene prompt contributes everywhere at strength 0.25; coral and stone prompts contribute at strength 1 under the soft band and its inverse. Including the full scene globally is intentional to give the material predictions shared context. This is a practical material-control recipe, not an isolated test of mask shape against the earlier background-only recipe.

The mask is a 170-pixel-wide rounded stroke along x=512+150*sin(2*pi*(y-160)/704), y=160..864, softened by a 12-pixel Gaussian blur. Coral and stone masks sum to one. The mask weights predictions; it does not guarantee object boundaries or unchanged pixels.

## Decision rule

Inspect all four outputs for a recognizable coherent face, coral following the drawn band, stone outside it, attractive integration and freedom from patch seams. Compare both seeds and show the target mask beside the outputs. If regional conditioning adds no useful shape control or causes obvious damage, park this experiment and retain complete prompts as the working default. Do not expand the test after seeing the results without a new decision.

## Execution

One owned L40S in US-TX-4 at a listed $1.09/hour plus 50 GB temporary storage. No existing Pods at preflight; account balance $36.94. Preserve the separate retained volume. Archive all four images and latents, the input mask, exact graphs, source copies, runtime/model receipts and remote/local hashes before deleting the owned Pod.

## Results and assistant review

All four prescribed images completed. Both methods produce recognizable, coherent stone faces with integrated coral and consistent painterly lighting. The regional versions contain the coral more tightly, preserve more exposed limestone and avoid the complete prompts' coral extending beyond the top-right and lower-left head silhouette. This effect repeats across both seeds without obvious rectangular patches or missing anatomy.

| Seed | Complete prompt | Regional material masks |
|---|---|---|
| 21001 | Rich branching coral crosses the nose and right-eye surround, extends beyond the upper-right forehead and sweeps down the outer left cheek. The face stays coherent. | Coral is contained to a smaller forehead/eye/left-cheek area, with more stone around it and an intact sculpted face. The lower return toward the centre of the chin is absent. |
| 21101 | A similar broad diagonal/curved coral path, with larger branches outside the head and extensive growth down the left cheek. | A tighter band across the forehead, nose bridge and left cheek; a few coral-like structures on the left cheek remain stone-colored. The lower chin section is again missing. |

**The mask changes coverage more convincingly than it reproduces the drawn shape.** Neither method completes the full S-shaped return to the centre of the chin. Both verbal controls already produce a similar sweeping composition, so this does not establish a capability that normal prompting cannot achieve. The regional images also change the sculpted head and hairstyle; same-seed text-to-image generation does not protect anatomy or pixels outside the mask.

The assistant prefers regional seed 21001 as a restrained material treatment, and complete seed 21101 as the more abundant coral alternative. These are taste judgments, not Olof's choices. The practical benefit is modest containment rather than reliable shape painting. Recommend parking this investigation and retaining complete prompts as the working default unless Olof specifically values the regional treatment. Human feedback on this final comparison is pending; no further generation is planned.

### Artifacts and reproduction

- [All four images with the target mask](../exports/krea-coral-v001/comparison.png).
- [Verified output inventory](krea-coral-inventory.json).
- [Executed API graph](../workflows/krea-coral.api.json) and [editable export](../workflows/krea-coral.json), from seed 21101.
- [Input mask](../workflows/krea-coral-band.png). Upload this filename into ComfyUI's input directory before running the exported graph.
- [Runner](run_coral.py) freezes the exact prompt text and generates the mask. [Review script](review_coral.py) verifies the archive and builds the comparison.

With an active prepared deployment receipt, run `uv run --script apps/comfyui/projects/regional-composition/experiments/run_coral.py run --deployment PATH_TO_ACTIVE_RECEIPT --seed 21001`, then repeat with 21101. The runner copies and verifies the mask before submitting. Use `collect --deployment PATH_TO_ACTIVE_RECEIPT --folder EXISTING_RUN` after a collection interruption; never blindly resubmit an ambiguous request. The closed deployment cannot run new jobs.

### Verification and cleanup

All four PNGs fully decode and were inspected at full resolution. All four native latents are also preserved. Every one of the eight remote output files matches its local SHA256. The input mask is copied into both run archives and verified against the remote input. Each run includes exact graphs, prompt/design metadata, node schemas, source copies and hashes, model manifest/verification, runtime statistics, history and submission/download receipts. The verifier confirms matched sampling parameters and that the complete-prompt sampler has no image or mask input. Complementary masks use the same loaded grayscale field and its inversion.

The API graphs executed successfully and editable exports were checked against live schemas; the exports were not reopened in the ComfyUI frontend. Input masks and comparison sheets are diagnostic artifacts, not additional model-generated images.

Runtime preparation took 28.29 seconds; model download/hash verification took 230.319 seconds. One small range-download probe succeeded while investigating the initially slow text encoder; the original download accelerated and finished without replacement. The two generation jobs, each containing both methods and their saves, took 37.447 and 22.960 seconds. Regional sampling evaluates three prompt predictions per step versus one for the control, so eight steps does not mean equal compute.

The owned Texas Pod `mty7l7t30wl62h` and its temporary storage were deleted after all output hashes matched and the queue was empty. A follow-up lookup returned 404. Approximately 10.33 minutes at the listed rate corresponds to $0.19 GPU compute, plus temporary storage; this is an estimate rather than an invoice. The separate retained network volume was untouched. Private receipts remain in `apps/comfyui/work/krea-coral/`.
