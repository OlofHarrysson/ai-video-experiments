# Prompting the opening and the next repaint

Research checked 2026-09-08. Companion to the [modern-model transition audit](modern-model-transition.md). These are source-backed practices and **untested draft prompts**, not a claim that wording alone fixes animation.

## Use the model's actual conditioning path

**FLUX.2:** BFL's current guide suggests starting with a clear subject and state, then adding concrete style, setting, lighting and composition. Add relevant information rather than stacking generic quality words. Its editing guide recommends specifying the requested change and what should remain. Those are family-level guidelines; do not import a hosted model's context-length or prompt-upsampling behavior into self-hosted Klein without inspecting the local graph. The old Klein-specific prompting URL now returns 404; current recommendations below come from the accessible official unified guide. [Prompt construction](https://docs.bfl.ai/guides/prompting_unified_building), [single-reference editing](https://docs.bfl.ai/guides/prompting_editing_single_reference).

The inspected Klein distilled workflow has CFG 1 with a zeroed negative conditioning branch. Our SDXL negative-prompt list would therefore not provide the same ordinary CFG steering. Describe the desired appearance positively. BFL's [technical guide](https://docs.bfl.ai/guides/prompting_unified_technical) also recommends this. This statement applies to the inspected recipe, not every base/distilled FLUX configuration or third-party guidance modification.

**Krea 2:** the author recommends natural-language descriptions, supports detailed prompts, and recommends quotation marks for rendered text. Both concise and paragraph-length artistic examples are provided. ComfyUI's official template includes optional **LLM prompt enhancement**, enabled by default according to its guide, and optional style LoRAs. A successful one-line demo may be passing a longer expanded prompt to the image model. For an interpretable first test, disable enhancement or expand once and archive/freeze the resulting text; do not independently expand every feedback frame. The template's apparent CLIPTextEncode node uses Krea's Qwen3VL encoder configuration, not SDXL CLIP weights. [Author prompt guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md), [ComfyUI controls](https://docs.comfy.org/tutorials/image/krea/krea-2).

**Z-Image-Turbo:** author examples use descriptive scene text and distinguish an optional prompt-enhancement process. Do not treat enhancement as an intrinsic property of every request. The native recipe's CFG 1 likewise gives no ordinary negative-branch steering. This remains a reserve model; no prompt-length optimum or feedback capability has been benchmarked here. [Author card](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo).

**SDXL:** it has useful creator recipes, as the [sampler research](model-sampler-recipes.md) shows. Tag-oriented descriptions and negative conditioning are features of our current setup, not evidence that all older models lack guidance or cannot understand sentences. We will preserve its successful recipe rather than continue a broad wording/sampler sweep before the new-model audition.

## A concrete issue in our existing prompt

The actual [current prompt](../../apps/deforum/projects/motion-guide-study/experiments/seed_comparison.py) repeatedly describes an empty black opening, although our selected image contains a central flame. It also places nebula wisps in the lower-left while the spatial transform changes the image. It was inherited from the opening recipe and remains constant through the latest tests.

**Hypothesis:** a static scene description that no longer describes the desired current frame may encourage reinterpretation or pull details back toward a fixed composition. This has not been isolated experimentally and is not a diagnosis of all observed drift. Simply shortening the prompt is not guaranteed to solve it. The more useful distinction is the prompt's job: establish a scene, or request a small edit to the supplied scene.

## Draft opening prompt

For the first Klein still, express a small number of concrete visual commitments:

> A hand-inked science-fiction illustration. A lone small explorer stands beneath a huge porous alien arch. One flame-shaped light floats inside the opening. Curled cables and perforated stone frame deep teal space. Thick black contours, fine engraved hatching and flat colors in burnt orange, pale cyan and ivory. Wide composition with the explorer near the lower center.

A longer comparison could add material texture and foreground/background relationships while retaining the same objects and layout. Avoid a simultaneous change of story, palette and medium. This is an authored test prompt, not copied from a creator example or a promised optimal length.

## Draft next-frame instruction

For a native editing model receiving the **already-warped** frame:

> Keep the explorer, framing, color palette and the arch's current curved shape. Refine the ink contours along the arch. Add a few delicate branching lines within the existing flame, retaining its outer silhouette and the hand-drawn appearance.

This makes the intended change concrete and distinguishes it from preserving the rest. It remains an experimental instruction: the model may alter more than requested. A reference editor should not be asked to “fix” or “improve” the entire frame when we want a narrow repaint.

For a conventional partial-img2img model, use a description of the intended resulting image; an imperative edit instruction is not automatically interpreted the same way. Do not transplant the Klein editing prompt into Krea's text-to-image graph and call that a matched editing test.

## Keep prompting controllable over time

Maintain a short stable description of medium/palette/subject, the intended content at the current point in the shot, and the requested change when the model supports editing. Spatial motion remains in our explicit controls. Avoid repeatedly asking for an incremental turn or enlargement after that operation has already been applied in pixels.

For each run, archive user-authored text, any expanded text, exact encoder/model recipe, reference image and prompt schedule. Changing prompts halfway through a shot should be a deliberate experiment with saved versions. Text-embedding interpolation is model-specific and remains deferred; longer natural-language descriptions do not establish that SDXL-style embedding blends transfer correctly.

Judge the opening separately from repeated edits: an attractive first still can still lose detail, erase the warp or drift toward a different subject after eight feedback steps. User playback preference determines whether the result is useful.
