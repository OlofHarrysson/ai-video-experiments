# Olof's reference: ControlAltAI area composition

Source: [ComfyUI: Area Composition, Multi Prompt Workflow Tutorial](https://www.youtube.com/watch?v=NPkSa1y0GLM), ControlAltAI, published 2023-11-18, duration 33:42. Olof supplied this as the tutorial he liked most when previously exploring regional prompting.

Read the complete description and untruncated English caption transcript on 2026-09-10. Metadata came from the YouTube Data API; the initial transcript API request failed with HTTP 429 and the skill recovered the caption track through yt-dlp. Local raw evidence is in ignored `apps/comfyui/work/youtube-reference/NPkSa1y0GLM-full.json` (12,977 transcript characters with timed caption entries). No audio transcription was required. This review covers description/transcript plus linked node source, not screen-by-screen inspection or execution of the creator's members-only JSON. Caption spellings of model names and technical terms can be imperfect.

## Main workflow

1. **Compose with regional prompts.** The first example uses ReV Animated (SD 1.5) at 512 resolution. One global background/theme prompt plus four regional prompts describe Red Riding Hood, a wooden house, the sun and the sky. Davemane42's MultiAreaConditioning provides a visual rectangle editor. Its output supplies the first basic KSampler's positive conditioning; the negative prompt is shared. These are simultaneous regional conditions, not sequential masked object insertions. At [6:48](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=408s), the narrator explicitly distinguishes this from noisy latent composition.
2. **Tune regional strength and geometry.** Start strengths at 1, then increase missing subjects selectively; the first subject is raised to 2, and the portrait example mentions needing as much as 5 in some cases. Broad left/right/center placement is described as easier than precise small-subject placement. Region canvas dimensions must match the generation canvas. Repositioning rectangles generates a different composition, not an exact move of an unchanged object.
3. **Upscale the latent and refine the complete scene.** At [11:06](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=666s), double the latent resolution and feed it to a second sampler. At [12:11](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=731s), construct a new, comprehensive positive text prompt describing the background and every subject together. This replaces the regional positive inputs for that pass. The first example reuses the negative prompt. The narrator tests normal at denoise 0.3, then exponential/Karras-related outcomes, and reports better detail above 0.44 after increasing denoise. That is an observation in this example, not a universal threshold or an exact recipe for SDXL.
4. **Optional further upscale/detail.** From [15:51](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=951s), use Ultimate SD Upscale with a Remacri upscaler and the comprehensive prompt. Start testing denoise around 0.3; excessive denoise adds unwanted content. Audition and settle the seed at each stage before continuing. A third pass is not always beneficial.

## Four examples

| Chapter | Scene | Added control |
|---|---|---|
| [1:51](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=111s) | Red Riding Hood, house, forest, sky and sun | Regional generation, latent upscale/global refinement, Ultimate SD Upscale; then rearrange house/subject/sun |
| [21:07](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=1267s) | Replace the sun with a volcano | Apply line-art/anime-edge ControlNet to that prompt branch; update later comprehensive prompts too |
| [25:11](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=1511s) | Magical bird facing a dragon, wide SDXL scene | Canny ControlNet on the bird branch to guide its orientation; raise missing-subject strengths |
| [27:18](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=1638s) | Portrait against Venice at night, Realistic Vision | Depth guidance from a portrait using MiDaS-derived depth; compare positions, strengths, seeds and refinement |

At [30:44](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=1844s), the narrator identifies poor blending without the second sampler and says a second pass is needed in most of their cases. At [31:40](https://www.youtube.com/watch?v=NPkSa1y0GLM&t=1900s), a centered portrait produces an unwanted crown from background lights; changing strength fails and changing seed is proposed. Global refinement is useful but can also misinterpret the composition.

## Difference from our baseline

Our selected regional result is a single-pass SDXL base image with full-canvas masked conditioning and background strength 0.25. The reference's first pass uses area conditioning, individually tuned foreground strengths, and tuned checkpoints. Its defining additional stage is **regional composition followed by a higher-resolution, whole-image resampling pass with one comprehensive prompt**. Our layered-inpainting branch's denoise-0.15 finish retained regional conditioning and used a different image construction process; it does not test this reference's refinement recipe. ControlNet and Ultimate SD Upscale were also absent from our baseline.

The reference supports testing that missing refinement stage on a saved regional output. This is a research recommendation; no new GPU session, installation or generation was performed for this review. The transcript does not establish exact rectangle overlap or every visible widget value, so inspect screenshots or the actual graph before claiming an exact reproduction.

## Description and implementation status

The description warns that the old node was no longer functional in the then-current ComfyUI as checked on 2024-08-10, while area conditioning remained available. It links the workflow JSON through YouTube membership, ComfyUI Manager, [Davemane42's nodes](https://github.com/Davemane42/ComfyUI_Dave_CustomNode), and [Ultimate SD Upscale](https://github.com/ssitu/ComfyUI_UltimateSDUpscale).

The Davemane42 repository is archived (2024-04-02). Its [source](https://github.com/Davemane42/ComfyUI_Dave_CustomNode/blob/main/MultiAreaConditioning.py) attaches region coordinates and strengths to separate conditioning entries; it does not implement successive object inpainting. Full-screen entries are passed through. Preserve the composition method when adapting it rather than assuming this historical UI extension will run unchanged today. Current compatibility was not execution-tested.
