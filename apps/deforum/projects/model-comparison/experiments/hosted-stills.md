# Hosted stills — 2026-09-06

Question: which model produces a useful lantern-marsh keyframe with distinct foreground, winding boardwalk, distant observatory, painterly texture and amber/teal lighting?

Initial RunPod Public Endpoints plan: one FLUX.1 dev image, one Seedream 4.0 image. Same exact positive prompt and seed 143; no negative prompt. The first FLUX request specifies 1024×576, 28 steps, guidance 7.5, PNG. Its documented dimensions must be multiples of 64, so the parent's 1280×720 overscan is not a valid exact match. Seedream requests 2048×1152 (16:9), one default output and enabled safety checking. Compare composition at the same display size; do not mistake a larger native image for a better sampler. A shared numeric seed does not yield shared latent noise across model families.

Estimated list cost: FLUX $0.01179648 at $0.02/MP; Seedream $0.027/image. The Seedream documentation's example response gives a contradictory higher cost, so record the actual response rather than treating the example as a quote. Authorized public-endpoint budget: $5. No provisioned resources or idle charges are expected from these public API calls.

fal experiment prepared separately: FLUX.2 pro 1280×720, seed 143, PNG; Seedream 5.0 Lite 2560×1440 (documented minimum total pixel area), `num_images=1`, `max_images=1`. Seedream's fal schema does not accept a seed or output-format input. Expected list cost $0.03 + $0.035 = $0.065. fal cap $2, separate account/billing. Initial key check found neither supported env name, so fal has not been invoked.

Before submission freeze exact prompt/params and the source recipe hash under `runs/`. Preserve every attempt. Review native images and common-size views. Record prompt fidelity, depth layers, painterly quality and defects separately. One still per model is a scene-specific sample, not a general model ranking.

Feedback suitability requires a different test: feed the same camera-warped anchor through a model's native editing API, then inspect a short repeated loop for composition drift, detail and flicker. Text-to-image endpoints expose no reference-image input. Hosted instruction editing does not establish SDXL-style denoise control, Difforum compatibility, temporal stability or comparable warm GPU costs.

Sources: [Flux Dev request and pricing](https://docs.runpod.io/public-endpoints/models/flux-dev), [Seedream 4 request and pricing](https://docs.runpod.io/public-endpoints/models/seedream-4-t2i), [fal Flux 2 schema](https://fal.ai/models/fal-ai/flux-2-pro/api), [fal Seedream 5 Lite schema](https://fal.ai/models/fal-ai/bytedance/seedream/v5/lite/text-to-image/api). Public schema/page snapshots are retained in `runs/preflight-2026-09-06/`.

## Executed outcome

Two FLUX calls and one Seedream call completed for $0.051 total reported cost. The initial FLUX request and a correction using the live schema's `aspect: landscape` both returned 1024×1024 JPEG with identical decoded pixels. The recipe now records the live `aspect` field; it does not promise landscape output. Seedream returned 2560×1440 JPEG, preserving 16:9 but increasing dimensions. All three attempts and two contact-sheet versions are retained. Seedream is the best match to this scene brief in static review; animation suitability remains untested. Full measurements, original links and API discrepancies are in the [session report](../../../../../docs/research/model-comparison-session.md).
