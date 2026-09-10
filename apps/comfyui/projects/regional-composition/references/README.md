# Reference evidence

- **Olof's preferred tutorial:** [ControlAltAI area composition](controlaltai-area-composition.md) — complete description/transcript review; regional composition followed by a comprehensive-prompt refinement pass, optional ControlNet and upscaling.

Retrieved 2026-09-10 from the official [Noisy Latent Composition page](https://comfyanonymous.github.io/ComfyUI_examples/noisy_latent_composition/).

- Original workflow-bearing image: [upstream PNG](https://comfyanonymous.github.io/ComfyUI_examples/noisy_latent_composition/noisy_latents_3_subjects.png).
- Local original: `assets/noisy_latents_3_subjects.png` (ignored media; drag into ComfyUI to load its embedded workflow).
- SHA-256: `48b60f8e0109527eeaadfb56e8ed2830c9b08e4de6ab722423f4daac06791a9a`.
- Both `workflow` and `prompt` JSON metadata were parsed locally. Extraction copies are in `apps/comfyui/work/regional-research/`.
- Observed graph node types: `CheckpointLoaderSimple`, `CLIPTextEncode`, `EmptyLatentImage`, `KSamplerAdvanced`, `LatentComposite`, `VAEDecode`, `SaveImage`.
- Inspected sampler widgets confirm early leftover-noise retention and continuation without new noise. The graph has three latent-composite nodes and one final decoder.

This is upstream artwork and workflow evidence, not a locally generated result. It references an older checkpoint that has not been installed by this task. Graph import, adaptation and current-runtime execution remain unverified.

Other sources and pinned-code findings are linked in the [research note](../../../../../docs/research/regional-composition.md).
