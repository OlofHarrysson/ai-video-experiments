# Lantern-marsh model comparison — 2026-09-06

**Produced three preserved images from two hosted model families for $0.051 in reported RunPod call costs.** Seedream 4.0 is the strongest match to this particular scene brief. FLUX.1 dev produced a clean image, but both attempts returned a square despite landscape controls. No provisioned worker, endpoint change, or fal call was needed.

[Contact sheet: four uncropped panels](../../apps/deforum/projects/model-comparison/runs/20260906T215546Z-contact-sheet-f04e03ad/contact-sheet.png) includes the parent's SDXL control. [Source manifest](../../apps/deforum/projects/model-comparison/runs/20260906T215546Z-contact-sheet-f04e03ad/sources.json) records dimensions and hashes. [Project and commands](../../apps/deforum/projects/model-comparison/README.md).

## Actual generations

All positive prompts exactly match the literal in `apps/deforum/projects/lantern-marsh/experiments/overscan.py`. Seed 143 was requested in all three calls. The numeric seed has no shared-noise meaning across different model families. RunPod does not expose immutable hosted model/checkpoint revisions; the names below identify the managed endpoints, not pinned weights.

| Model / attempt | Requested | Downloaded original | API-reported cost | Queue / execution |
| --- | --- | --- | --- | --- |
| FLUX.1 dev / size fields | 1024×576, 28 steps, guidance 7.5, seed 143, PNG | **1024×1024 JPEG** | $0.012 | 4.876s / 16.663s |
| FLUX.1 dev / aspect correction | `aspect: landscape`, 28 steps, guidance 7.5, seed 143, PNG | **1024×1024 JPEG** | $0.012 | 6.883s / 9.926s |
| Seedream 4.0 T2I | 2048×1152, seed 143, safety checker enabled | **2560×1440 JPEG** | $0.027 | 5.040s / 14.454s |
| SDXL base 1.0 / parent control | 1280×720, 28 steps, CFG 6.5, DPM++ 2M/Karras, seed 143 | 1280×720 PNG | Parent accounting | Parent accounting |

Originals and exact API evidence:

- [FLUX initial image](../../apps/deforum/projects/model-comparison/runs/20260906T215105Z-flux-dev-04aa5c65/original-00.jpg); run `20260906T215105Z-flux-dev-04aa5c65`.
- [FLUX landscape-attempt image](../../apps/deforum/projects/model-comparison/runs/20260906T215346Z-flux-dev-1ba040db/original-00.jpg); run `20260906T215346Z-flux-dev-1ba040db`.
- [Seedream image](../../apps/deforum/projects/model-comparison/runs/20260906T215118Z-seedream-4-f5a8fd86/original-00.jpg); run `20260906T215118Z-seedream-4-f5a8fd86`.
- [Parent SDXL image](../../apps/deforum/projects/lantern-marsh/runs/20260906T214815368534Z-overscan-1f/frames/0000.png), read without editing its source or receipt.

Each hosted run contains `request.json`, `receipt.json`, `reservation.json`, `submission.json`, timestamped statuses, `result.json`, `artifacts.json` and `inspection.json`. These preserve exact prompts, parameters, source URLs, request IDs, costs, actual dimensions and SHA-256 hashes. Everything in `runs/` is ignored by Git. All generations, including both FLUX attempts, remain intact.

## Dimensions and API drift

The [official FLUX docs](https://docs.runpod.io/public-endpoints/models/flux-dev) document `width`/`height`, so the first call used 1024×576 (valid multiples of 64). It returned 1024×1024. The live [FLUX playground](https://console.runpod.io/hub/playground/image/black-forest-labs-flux-1-dev) embeds a different schema: it has a required `aspect` string, default `square`. Its visible controls offer Square/Landscape/Portrait. Selecting Landscape generates a code example with width 1024 and height 768, further demonstrating inconsistent interfaces.

The one corrective call used `aspect: "landscape"`, omitting width/height. It also returned square. Decoded RGB pixels are **exactly identical** between the two FLUX images (mean absolute difference zero in all channels); JPEG file hashes differ. Thus this is two preserved requests but one unique visual result. Landscape control is unresolved at the provider interface; the correction is not claimed as successful. Both calls returned JPEG despite requesting PNG.

The [Seedream docs](https://docs.runpod.io/public-endpoints/models/seedream-4-t2i) accept a `width*height` size string without stating bounds. The playground's embedded schema lists only square presets. The actual 2048×1152 request returned 2560×1440: aspect ratio was retained, pixel dimensions were not. Its internal resizing behavior was not investigated further.

Both live endpoints return the output URL as `output.result`; documentation uses `output.image_url`. Initial downloads stopped on that schema mismatch. The collector was corrected and recovered both completed jobs without resubmission. The corrected response reader is the single implemented path for these verified endpoints.

The FLUX list price is $0.02/MP, but returned cost was $0.012 per square 1.048576 MP image. That does not reconcile with actual output area; it nearly matches the first requested 0.589824 MP area after rounding, but the second call omitted dimensions and was charged the same. Preserve reported costs rather than inferring the billing formula. The combined $0.051 is the sum of three job receipts, not a reconciled account-ledger delta. Other agents were running concurrently. Pre-call balance was $49.6992503705; account-wide spending cannot be attributed using a later balance alone.

## Static image review

| Scene criterion | SDXL control | FLUX.1 dev | Seedream 4.0 |
| --- | --- | --- | --- |
| Copper lantern in left foreground | Missing; lit pavilion dominates | Clear hanging lantern | Large, strongly framed copper lantern |
| Winding boardwalk and distant dome | Short straight boardwalk; pavilion is near | Clear winding path; dome fairly large | Strong winding path toward smaller distant dome |
| Crescent moon | Large full luminous disk | Full moon | Clear crescent |
| Blue mushrooms / violet mist | Not evident | Mushrooms resemble amber path lamps; blue haze | Blue mushrooms and violet mist are explicit |
| Painterly texture | Graphic illustration with broad color shapes | Smooth, crisp, detailed scene | Visible brushwork in sky, reeds and boardwalk |
| Depth separation | Foreground reeds, water and pavilion | Strong path perspective, foreground tree and reeds | Strong lantern/reeds, winding path, distant observatory |

For this prompt, choose the **Seedream image as a candidate keyframe**. Its saturated blue mushrooms and purple mist may need taste adjustment; the close lantern occupies a large part of the frame. FLUX is more restrained but misses several explicit details. SDXL has a coherent graphic style while departing more from the scene instructions.

These are single-prompt observations, not overall model rankings. SDXL also used its existing negative prompt and different sampler/conditioning. Seedream has 3.52× the native pixel count of FLUX; the contact sheet fits each entire image into equal panel bounds without cropping, stretching, sharpening or recoloring. This makes layout and content visible, but is not a resolution-matched quality test. Native originals are retained for detailed review. No user playback review or animation generation occurred in this comparison.

## Feedback animation and cost

The tested APIs were **text-to-image**. Neither tested call accepts a warped reference frame. They do not validate recurrent img2img, denoise strength, explicit camera warps or Difforum integration.

Separate hosted editors exist: [FLUX Kontext dev](https://docs.runpod.io/public-endpoints/models/flux-kontext-dev) at $0.025/image and [Seedream 4 edit](https://docs.runpod.io/public-endpoints/models/seedream-4-edit) at $0.027/image. These are instruction-based reference editing APIs, with no documented SDXL-equivalent denoise control. Neither was invoked here. Kontext is a different model from the FLUX dev T2I endpoint.

At list price, 39 editor calls would cost $0.975 or $1.053, approximately 32× or 34× the repository's $0.0309 warm SDXL five-second baseline. This is an economic illustration with differing outputs and resolution, not a matched animation benchmark. An occasional Seedream keyframe is inexpensive; using a hosted editor on every generated frame is outside the project's near-SDXL recurring-cost target. The next useful experiment is a short SDXL continuation from this Seedream keyframe, owned by the parent, followed by a native model feedback test only if justified.

## fal recipe and validation

`FAL_KEY` and `FAL_API_KEY` were absent from process environment and the known repo/app `.env` locations. The parent was notified promptly. No other credential locations were searched; fal spend is **$0**.

[The recipe](../../apps/deforum/projects/model-comparison/experiments/hosted_stills.py) also prepares FLUX.2 pro (1280×720, seed 143, PNG) and Seedream 5.0 Lite (2560×1440, `num_images=1`, `max_images=1`). Seedream 5 Lite's current fal schema has no input seed or output-format field. These are newer named variants than the RunPod models actually tested. Public list estimates total $0.065; fal has its separate $2 cap. Sources: [FLUX.2 pro](https://fal.ai/models/fal-ai/flux-2-pro), [Seedream 5 Lite](https://fal.ai/models/fal-ai/bytedance/seedream/v5/lite/text-to-image).

Preflight snapshots and frozen fal request JSON live under `runs/preflight-2026-09-06/`. Request keys and required fields were checked against the downloaded current OpenAPI schemas. The unexecuted fal transport remains unverified with a real account.

Validation completed: actual remote image generation, original downloads, decoded dimensions/formats, exact prompt equality against the parent, RGB comparison between FLUX attempts, SHA-256 preservation, collection recovery without generation, and visual inspection of images/contact sheet. No commits, pushes, shared-code changes, or infrastructure mutations were performed by this task.
