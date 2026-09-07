# Mechanical to organic opening

Status: six original stills and two six-second videos rendered and preserved. Version v002 is the assistant-selected study cut; neither video meets the reference-quality target yet.

## Hypothesis

The SDXL art LoRA credited by the reference creator, a simple moving silhouette and QR ControlNet can combine confident illustrated detail with deliberate shape transformation. Compare three stills using identical seed 7301, prompt, guide, CFG 7, 32 steps and control strength 0.65; LoRA weights are 0, 0.7 and 1.1. Select by visual resemblance, then test 48 frames at 8 generated FPS (six seconds, 24 FPS repeated-frame delivery).

The first animation uses incrementing seeds, 30 steps, denoise 0.55, control strength 0.75, noise 0.025 and sharpening 0.35. A tiny 1.001 zoom accompanies the guide's circle-to-slit-to-organic-circle change. This is a controlled silhouette transformation, not proof of a reconstructed 3D scene. Review whole clip plus densely sampled transitions; revise only against a visible problem. User authorized the remaining RunPod learning balance; opening balance $48.06952 with no active spend.

## Model provenance

- SDXL base and Difforum remain pinned in the worker Dockerfile.
- Creator-credited [art LoRA, version 152309](https://civitai.com/api/v1/model-versions/152309): SHA-256 `15e31fe2b6ae2e77ee47a3ccdf27bd14f7b54ce27c6a58502875fdad26f34460`. Civitai download requires authentication; a [public Hugging Face copy](https://huggingface.co/frankjoshua/xl_more_art-full_v1/blob/a534d8341d2741fab30581e12fae1e38b38a23cc/xl_more_art-full_v1.safetensors) has the identical hash. Build checks it.
- Creator-credited [QR ControlNet, version 165780](https://civitai.com/api/v1/model-versions/165780): source SHA-256 `7000c1bbbbea48201782f018618a60f8a5fde25b2a0970f790cd192f0dd5f00f`. Its header mixes original UNet names with four Diffusers `add_embedding` names. Build conversion follows [ComfyUI v0.34.0's mapping](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/utils.py) to `label_emb`; tensor payload is copied unchanged. Runtime inference must still establish compatibility.

## Runs and findings

All four jobs completed and were collected with manifest checksum verification. Sources, executed workflows, input guides and intermediate attempts are retained locally. Timestamped frame inspection supports the findings below; perceived smoothness/flicker still needs Olof’s playback judgment.

## Setup timing and iteration

The first expanded worker build (`f106834`) took 18m55s (06:47:44–07:06:39 UTC), including base-layer downloads, added model downloads, conversion, CPU startup check, export and upload. This is build time, not diffusion time. Initial worker startup then downloaded and extracted the image on an uncached host. Record job queue delay separately from execution duration. Prompts, graph connections and sampling settings are request data and require no build when the required nodes/models are already installed.

The initial Dockerfile put QR conversion in a later layer, retaining an unnecessary 5,004,160,600-byte source file in image history. The revised Dockerfile downloads, converts and removes that intermediate within one layer. This fix is not in the image used for the first study runs; it applies to a subsequent build. A temporary 120-second idle window allows visual review between jobs; restore five seconds and pause workers at cleanup. Keep the same model/tool image throughout a creative session.

### Still selection

First sweep `20260907T071248591219Z-stills-lora-sweep-3f`: compatible runtime; all three images rendered. Warm/cold job values: 390.206s delay, 20.931s execution. The palette and linework are promising, but wheel spokes block the focal opening. Second sweep `20260907T072106682696Z-stills-control-sweep-3f` revises the prompt/negative prompt and holds LoRA at 1.1 while testing QR strengths 0.25/0.40/0.55. Delay 0.111s, execution 12.581s. Candidate D (index 0, strength 0.25) is selected by the assistant: open portal, orange focal point, visible small figure and dark surroundings. Neither sweep yet reproduces the reference’s porous, asymmetrical richness. No user approval of these individual candidates is inferred.

First feedback render uses candidate D, denoise 0.55, QR strength 0.75 and the original moving silhouette. The guide constrains the transformation more strongly than in the still test; inspect the first few frames for a composition jump and late frames for detail loss.

### First animation and targeted revision

`20260907T072220823026Z-feedback-v001-48f`: 48 source frames, 6 seconds; delay 0.145s and execution 174.063s. Timestamped review covers the whole clip plus 0.125/0.25s and 2.875/3/3.125s. The inner aperture visibly narrows and reopens, but the large outer body remains frontal. Detail drains away quickly, the figure disappears, and the later portal becomes smooth flat bands and a pale scalloped insert. Graphic palette persists, but sustained detail and reference richness fail. This is not a successful reproduction.

Revision v002 uses the same anchor, guide, seed schedule, prompts and LoRA, changing denoise 0.55→0.82 and ControlNet 0.75→0.40. Hypothesis: stronger image regeneration with less silhouette constraint can preserve/invent richer texture and organic shapes. This paired change tests the balance of repainting versus structure; it does not isolate either parameter. Increased temporal variation is expected and must be judged in playback.

### Revised animation

`20260907T072631982593Z-feedback-v002-48f`: 48 source frames, six seconds; delay 0.136s, execution 172.596s. Stronger repainting creates more variation and organic contours near the end. Mechanical detail is richer through roughly the first 1–1.6 seconds, but the midpoint again reduces to large smooth teal/cream/orange regions. A darker irregular opening and rippled contour detail return later. The tiny explorer is not maintained. The result establishes controllable shape evolution and a promising palette, not the reference’s dense continuous illustrated invention.

| Criterion | v001 | v002 |
| --- | --- | --- |
| Palette / bold outline | Retained | Retained |
| Deliberate aperture change | Narrows and reopens | Narrows, develops organic edges, reopens |
| Sustained detail | Fails: smooth bands dominate | Fails at midpoint; partial late recovery |
| Figure / spatial continuity | Figure disappears | Figure disappears; world changes more |
| Reference match | Partial visual traits only | More promising movement, still insufficient richness |

No optical-flow interpolation is applied. Both have eight generated frames per second delivered at 24 FPS through repetition. The reference study copy is 60 FPS delivery; its generated FPS/interpolation are unknown. These are sampled-frame findings, not a claim that flicker, tempo or full playback quality is solved.

## Outputs

- [All six original stills](../exports/all-stills.jpg).
- [v001 video](../exports/v001/preview.mp4), [cut and source range](../cuts/v001.md), [timestamped review](../exports/feedback-v001-review/v001/review.json).
- [v002 video](../exports/v002/preview.mp4), [cut and source range](../cuts/v002.md), [timestamped review](../exports/feedback-v002-review/v001/review.json).
- [Reference versus generated frames](../exports/reference-comparison.jpg); reference frame remains attributed to PintoCreation, YouTube drUsc1Vfy6s at 36s. It was never used as a generation input.

## Next hypothesis

Replace the sparse binary silhouette with a richer sequence of illustrated intermediate keyframes or a structured hybrid guide, while keeping the prepared model stack. The current guide controls the aperture but contributes little evolving scene content; stronger repainting alone did not sustain detail. Test a short transition between two visually convincing states before extending the shot. This is a proposal, not a tested fix. Normal-speed playback of these two versions should inform the next choice.

## Validation and cleanup

All four GPU jobs completed. Both cuts have 48 preserved source frames and six-second H.264 previews. The local suite passed all 17 tests with Pillow enabled; a focused conversion check verified the four renamed header keys and unchanged tensor payload. Native ComfyUI inference establishes that the converted model loads and runs, beyond the earlier CPU startup check. All 122 cloud objects (105,018,956 bytes) were compared byte-for-byte with local archives, including requests and auxiliary files; a second inventory confirmed the volume was unchanged. Workers were set to min/max zero, idle timeout restored to five seconds, volume detached and deleted. Worker, Pod and volume inventories were empty. Private job, build, storage and account receipts remain in ignored `work/brain-entity-session/`.
