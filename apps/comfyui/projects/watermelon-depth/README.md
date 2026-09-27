# Watermelon placement from authored depth

Approved 2026-09-27: test whether Krea 2 Turbo turns a simple sphere-depth guide into one watermelon at the guide's position and size. This is a still-image feasibility test for later Remotion-authored motion and recurrent Deforum painting.

**Result:** all eight images completed, but this recipe failed to follow the guide's position and size. The owned GPU is removed and all outputs are preserved. [Comparison, evidence and next diagnostic](results.md).

**Author-example follow-up:** the original dog-to-lion example completed through the author's hosted pipeline. Broad placement survives; head pose changes substantially. Our ComfyUI integration remains unvalidated. [Reproduction and comparison](author-reproduction.md).

## First experiment

- Six controlled images: left, centre and right sphere positions, each with seeds 21001 and 21101.
- Two complete-prompt baselines: the same seeds, without the depth adapter.
- Fixed 1024-square canvas, radius 180 pixels, centre y=512, x=256/512/768. Near surfaces are white. The guide represents orthographic viewing of a sphere with centre depth 4, radius 1 and background depth 8; inverse depth is normalized globally to 0–1.
- One identical prompt, Krea Turbo FP8, Qwen3VL encoder, Qwen Image VAE, eight Euler/simple steps and CFG 1. Full generation from noise; no previous painting, image initialization or motion in this experiment.
- Controlled branch: Patil/Krea-2-depth-controlnet at strength 1. The baseline bypasses both adapter and control image. This compares the complete guided recipe with ordinary generation, not an isolated input-only ablation.

Success means one recognizable whole watermelon follows all three positions in both seeds, with useful agreement in centre and silhouette. Inspect every image, compare guide overlays, and report exceptions. Do not extend into animation or sweep settings automatically if this fails.

## Sources and execution

- [Depth adapter](https://huggingface.co/Patil/Krea-2-depth-controlnet), revision `21889413aa7282a6e78bd510247cceccad034b24`, SHA256 `fb80547ed79b47c1e3fea7bb9d36297e3917b2115fab6700ca1501350f9f483c`.
- [ComfyUI nodes](https://github.com/facok/comfyui-krea2-controlnet), commit `79ebfd3bd80d2180b334dd7ce57f3c9ddaa0848f`.
- Reuse the pinned Krea assets and ComfyUI runtime from the [Pod runbook](../../../deforum/POD.md). RunPod RTX 4090 listed at $0.74/hour; retain the shared model volume and remove the owned Pod after verified collection.
- The model author's eight-step Turbo claim is the starting recipe. Our three-step recurrent animation recipe has not been validated with this adapter.

Run records, graphs, guide originals, node source and image hashes belong in ignored `runs/`; comparison sheets in ignored `exports/`. Private resource receipts belong in `apps/comfyui/work/watermelon-depth/`.
