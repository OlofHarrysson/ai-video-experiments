# ComfyUI YouTube research: gradual surreal morphing

Research date: **2026-09-07**. This is a transcript and author-artifact study, not a playback review or a tested workflow. Eleven complete available caption tracks were read; no GPU jobs or workflow implementations were run.

## Practical findings

**Keep the gradual transformation in P01/P03/P04 as the artistic target. Treat P06 as a detail diagnostic, not the preferred animation.** Olof's latest feedback supplied for this research—P06 is clear but feels like a slideshow—takes precedence over the earlier candidate-baseline wording in the [parameter study](../../apps/deforum/projects/brain-entity-study/experiments/parameters.md).

The useful YouTube material points toward **directing what changes over time**, while keeping style and structural constraints separately adjustable. It does not establish a better universal denoise/CFG/steps recipe, or a proven replacement for our feedback loop.

1. **Reference conditioning can supply a transformation path.** Latent Vision demonstrates transitions between reference images using evolving attention masks, then adds structural conditioning where a logo needs to remain recognizable. The demonstration uses SD1.5 AnimateDiff, not recurrent SDXL. The transferable hypothesis is a controlled handoff between visual concepts; the graph and settings are not directly transferable. [Animation tutorial, 00:40–11:30](https://www.youtube.com/watch?v=ddYbhv3WgWw&t=40s).
2. **Style, composition, and structure need different controls.** The IPAdapter developer's SDXL examples separate style/composition inputs and combine image conditioning with lineart, Canny or depth. The author repeatedly adjusts the prompt, reference and conditioning together. This supports testing a consistent style anchor alongside changing subject content; it does not prove that IPAdapter preserves engraved detail across many feedback iterations. [Style tutorial, 12:41–18:40](https://www.youtube.com/watch?v=gmwZGC8UVHE&t=761s), [author's workflow archive](https://f.latent.vision/download/style_transfer.zip).
3. **Eight generated FPS remains eight distinct images per second when repeated at 24 FPS.** Interpolation can add intermediate images for presentation. It cannot establish a good semantic transformation between poor endpoints. A comparison on preserved P01/P03/P04 source PNGs would isolate presentation smoothness without another diffusion render. This is a proposed diagnostic, not a quality prediction. [RIFE tutorial](https://www.youtube.com/watch?v=LHunwnT2afc), [VideoHelperSuite frame-rate semantics](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite#io-nodes).
4. **A convincing “ComfyUI film” may use a different animation engine.** Mickmumpitz uses Blender layouts and ComfyUI to render poses, but identifies Kling as the tool creating the movement between start/end images. The SDXL graph is useful evidence for structural guidance; the finished film is not evidence that this graph alone makes gradual recurrent animation. [Explicit handoff at 22:08](https://www.youtube.com/watch?v=PZVs4lqG6LA&t=1328s).
5. **Several beginner explanations are too literal for engineering decisions.** Denoise is not an old/new pixel percentage; “same seed” is not a cross-runtime determinism guarantee; a batch of images is not previous-frame feedback. Use the [pinned local parameter audit](feedback-parameters.md) for our sampler semantics, and tutorials for concrete ideas and failure examples.

Our baseline for interpreting these findings is Difforum `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`, ComfyUI `0.34.0`, SDXL base plus art LoRA, cadence 1, incrementing diffusion/image-noise seeds, denoise 0.82, CFG 7, and 8 generated FPS repeated at 24 FPS. Existing source-audit work owns the exact Deforum/Difforum comparison; this report does not replace it.

## Coverage and selection

The first pass used **10 queries, up to 5 results each**, relevance ordering, English relevance, and publication dates from 2025-01-01 through the retrieval date. The API returned **46 results**, all unique; the gradual-morph query returned only one result. A focused, age-unrestricted pass used **6 queries, up to 5 each**, returning **25 results**. Across both passes there are **69 unique candidates**, plus one animation tutorial linked directly from the IPAdapter author's README: **70 unique videos** in the final corpus.

Of **12 videos selected for enrichment**, **11 yielded complete available caption tracks**, with no character truncation: **150,201 transcript characters and 4,105 timestamped snippets**, covering videos with a combined listed duration of **3 h 1 m 34 s**. Six successful videos are from 2025–2026; five are older specialist foundations. This duration is not time spent watching. Comments requested: **zero**.

The ten initial queries were:

```text
ComfyUI image to image animation feedback loop
ComfyUI Deforum morph animation workflow
ComfyUI prompt travel scheduling animation
ComfyUI gradual morph animation interpolation
ComfyUI IPAdapter style composition animation
ComfyUI ControlNet animation consistency tutorial
ComfyUI noise seed denoise sampler explained
ComfyUI custom nodes workflow troubleshooting
ComfyUI frame interpolation RIFE tutorial
ComfyUI animation workflows advanced tutorial
```

The follow-up queried Latent Vision style/composition, Latent Vision noise, ComfyUI Deforum, FizzNodes scheduling, recursive feedback, and official troubleshooting. Exact query strings, filters and per-query counts are in the archived search metadata below. Recent broad searches were noisy: native Wan/Kling workflows, character consistency, unrelated architecture videos and shorts crowded out recurrent image-loop techniques. The focused pass recovered more relevant older material. This is a bounded purposive sample, not a representative survey of ComfyUI or a census of channels.

### Trust rubric

Trust is **claim-specific**, assessed in this order:

| Criterion | What counted |
| --- | --- |
| Implementation proximity | Maintainer/author identity connected to a repository, or an official channel linked by the product's own site. |
| Reproducible artifact | Accessible workflow JSON, source code or a precise upstream node reference that can be inspected. |
| Explanatory quality | Named inputs/models, visible-in-narration troubleshooting, limitations, and distinctions between components. |
| Fit to this task | SDXL image processing, temporal schedules, feedback or frame handling; native video alone receives low transfer confidence. |
| Freshness | Publication date plus retrieved artifact/version evidence. A recent title does not override an old graph or incorrect explanation. |
| Incentives and independence | Sponsorship, hosted-service promotion and paid workflow tiers recorded; same-author videos are not independent corroboration. |

Views, likes and search repetition remain in metadata but did not determine technical trust.

| Source | Assessment and selected use |
| --- | --- |
| **Latent Vision / Matteo / cubiq** | Highest implementation proximity for IPAdapter: the [repository](https://github.com/cubiq/ComfyUI_IPAdapter_plus) links his tutorials, which link back. Four full transcripts; free author workflows downloaded. Strong conceptual and node-specific evidence, with explicit age/version caveats. |
| **Mickmumpitz** | Strong practical workflow provenance: [dated author post](https://www.patreon.com/posts/123836639) and downloadable SDXL JSON. Useful separation of layout, rendering and motion. Paid advanced tier disclosed; film quality not independently viewed. |
| **Sebastian Kamph / Floyo AI collaboration** | Useful specialist instruction on graph literacy and current frame I/O. Floyo's description explicitly credits Kamph; his own descriptions promote hosted services/Patreon. Three transcripts, **one author**, with material denoise simplifications identified below. |
| **Olares × SweetValberry** | Narrow, well-specified RIFE instruction linked to the actual node repository. Vendor tutorial and auto-dubbed narration, not RIFE authorship or a measured quality benchmark. |
| **Rob Adams** | Useful exploratory technique because the actual shared JSON could be downloaded. Claims about better blends or broad model compatibility remain practitioner observations, not controlled comparisons. |
| **Shiccup** | Directly relevant historical Deforum walkthrough, linked to XmYx's repository. Valuable troubleshooting testimony; unclear parameter explanations and admitted experimentation make it unsuitable as semantic authority. |
| **CG TOP TIPS** | Selected for prompt scheduling, but transcript recovery failed. Metadata and description only; no detailed tutorial conclusions attributed to it. |

The verified official channel is [@comfyorg](https://www.youtube.com/@comfyorg), linked by [Comfy's own community page](https://docs.comfy.org/community/links). Search candidates included [Repeat One Image for Animation](https://www.youtube.com/watch?v=vSPpmqIllB0), 2025-07-17, 00:41, and [Preprocessors & Frame Interpolation Workflows](https://www.youtube.com/watch?v=cXA0C08pw7Q), 2026-01-14, 00:34. They remain **metadata-only orientation**, not deep tutorial evidence. The [official-source ComfyUI report](comfyui-animation-practices.md) covers current documentation and source compatibility.

## Transcript-backed video notes

Times below are caption offsets or author chapters, rounded for navigation. They identify narrated passages, not independently verified on-screen results. Original caption spelling is preserved privately; technical names here are normalized using linked artifacts. Each full transcript has a corresponding `videos/VIDEO_ID.json`, plain text file and timed JSONL in the ignored corpus.

### V01 — Style and Composition with IPAdapter and ComfyUI

[Latent Vision · 2024-04-04 · 09:40](https://www.youtube.com/watch?v=czcgJnoDVd4)

- **00:26–03:05:** SDXL style transfer attempts to carry visual treatment while changing the subject; small weight changes materially affect the author's examples.
- **03:05–04:56:** Composition transfer leaves more reinterpretation than the author's ControlNet comparison.
- **04:56–08:40:** Separate style/composition images and weights; expanding style affects more SDXL layers. Better prompting remains necessary.

**Artifact check:** The author's repository contains `IPAdapterStyleComposition` and a matching example; the downloaded example is archived at commit `a0f451a5113cf9becb0847b92884cb10cbdec0ef`. [Example JSON](https://github.com/cubiq/ComfyUI_IPAdapter_plus/blob/a0f451a5113cf9becb0847b92884cb10cbdec0ef/examples/ipadapter_style_composition.json).

**For our loop:** a possible way to distinguish an art-style anchor from changing scene composition. This is still-image evidence. Repeated application might also resist desirable morphing or introduce content from the style image. No successful recurrent run is shown by this research.

### V02 — Become a Style Transfer Master with ComfyUI and IPAdapter

[Latent Vision · 2024-04-15 · 19:02](https://www.youtube.com/watch?v=gmwZGC8UVHE)

- **00:16–08:52:** Lineart plus style conditioning; conflicting references require adjustment rather than one fixed configuration.
- **08:52–12:41:** Depth-conditioned masked material replacement, then mask growth and Differential Diffusion for boundaries.
- **12:41–17:02:** Existing-image stylization; Canny and depth have different roles. Ending depth guidance early gives the model room to reinterpret.
- **17:02–18:40:** Style references can leak their subject; negative image conditioning is offered as a mitigation.

**Artifact check:** The [free ZIP](https://f.latent.vision/download/style_transfer.zip) downloaded successfully and passed ZIP integrity checking. Four JSON workflows confirm `IPAdapterStyleComposition`, ControlNet, preprocessing and the masked inpainting path.

**For our loop:** the most directly useful SDXL reference-conditioning lesson in this set. It motivates a conditional style-anchor experiment, not an immediate node addition. Its caution about very few-step models concerns fine control; it does not invalidate our ordinary SDXL 15-step P04 test.

### V03 — Infinite Variations with ComfyUI

[Latent Vision · 2023-11-25 · 16:25](https://www.youtube.com/watch?v=Ev44xkbnbeQ)

- **03:13–06:17:** Separate text-conditioning paths and timing change the generated variations.
- **06:17–08:33:** Splitting a sampling trajectory and resuming with a stochastic sampler produces variations.
- **09:30–13:59:** Unsampling followed by resampling; mismatched schedules produce bad results in the narrated example.
- **13:59–15:48:** Mix a stable base noise field with varying noise using SLERP, then inject it with an appropriate sigma.

**Artifact check:** [ComfyUI_Noise](https://github.com/BlenderNeko/ComfyUI_Noise) documents matching noise, sigma, injection and unsampling operations. Its README says the old duplicate-batch functionality moved into core; old node names should not be copied blindly.

**For our loop:** correlated noise is a more meaningful research direction than assuming adjacent seed integers produce adjacent images. This is a hypothesis about temporal input design; the video demonstrates image variations, not our recurrent animation. SDXL conditioning-resolution tips and “horror negatives” are local observations, not recommended settings.

### V04 — Animations with IPAdapter and ComfyUI

[Latent Vision · 2023-11-30 · 16:07](https://www.youtube.com/watch?v=ddYbhv3WgWw)

- **00:40–04:10:** A text-only cat/dog morph is insufficient; complementary moving reference masks and a less forceful adapter improve the narrated attempt.
- **04:10–08:40:** Logo/eye transformation adds masked Tile ControlNet; stronger reference fidelity can be useful locally.
- **08:40–11:30:** Changing 16 to 32 output frames also requires attention to mask length. A short mask batch repeats its final mask in this historical implementation.
- **11:30–15:20:** Batched reference images can be interpreted jointly or unfolded across frames; a blink sequence illustrates their difference.

**Artifact check:** The [IPAdapter README](https://github.com/cubiq/ComfyUI_IPAdapter_plus#video-tutorials) links this as an animation tutorial and explicitly labels it a previous-version video.

**For our loop:** strongest concrete morph-direction example, but its SD1.5 AnimateDiff temporal mechanism is a major compatibility boundary. The 16-frame advice is historical model-context advice, not a general clip-length limit. Transferring masks into a recurrent sampler requires explicit per-frame evaluation.

### V05 — Comfyui Deforum: A Detailed Tutorial / trouble shooting guide

[Shiccup · 2024-04-05 · 09:12](https://www.youtube.com/watch?v=QHNTGvaH7OE)

- **00:49–03:14:** Starts from packaged example workflows; discusses auto-queue, cached video frames, counter/latent resets and prompt formatting failures.
- **03:14–06:33:** Experiments with hybrid motion and cadence while acknowledging uncertainty. Lightning settings belong to that checkpoint.
- **06:33–07:34:** Dumps cached frames and changes export encoding after an unreadable output.

**Artifact check:** The description links [XmYx/deforum-comfy-nodes](https://github.com/XmYx/deforum-comfy-nodes), not the pinned Difforum package. Its exact source semantics are deferred to the separate audit.

**For our loop:** useful evidence that graph state, frame counters, prompt syntax and export behavior matter. Its loose descriptions of strength, noise and cadence are not sufficient definitions. Do not transfer auto-queue instructions to our single serverless feedback job or interpret the video as proof of reliable hybrid motion.

### V06 — Control MULTIPLE CONSISTENT CHARACTERS + CAMERA with this FREE AI Workflow

[Mickmumpitz · 2025-03-07 · 26:31](https://www.youtube.com/watch?v=PZVs4lqG6LA)

- **08:56–09:40:** Blender blocking establishes poses, camera and lighting before AI rendering.
- **11:50–13:40:** ControlNet strength decreases during image sampling; seeds and additional refinement still matter.
- **16:28–19:55:** SDXL alternative uses reference images, Tile/Canny guidance and regional masks.
- **22:08–24:33:** Kling creates movement between rendered poses; independently repainting movie frames is a separate stylized accent.

**Artifact check:** The [public author post](https://www.patreon.com/posts/123836639) supplied `250307_3D2IMG_v01_SDXL_SMPL.json`. Its 172 nodes include IPAdapter, advanced ControlNet, timestep interpolation, segmentation, sampling and image output. It is an inspectable still-rendering graph, not a recovered recurrent-loop implementation.

**For our loop:** supports the distinction between controlled structural inputs and diffusion styling. Timestep keyframes here operate **within a denoising pass**, not across movie frames. Blender guidance remains a later hypothesis; this corpus does not overturn the project's decision to establish short morphs first.

### V07 — How to use ComfyUI for beginners

[Sebastian Kamph · 2025-04-19 · 39:12](https://www.youtube.com/watch?v=23VkGD-4uwk)

- **01:31–03:21:** Loading a workflow, missing nodes, model acquisition, restart and browser refresh.
- **16:25–23:07:** Image/latent/conditioning connections and differences between SDXL checkpoint loading and separate Flux components.
- **24:13–31:31:** Seed, steps, CFG and sampler overview.
- **31:31–36:45:** Image-to-image examples explain denoise using a retained/rebuilt percentage metaphor.

**Validation:** The topology lesson is useful; the percentage metaphor is not the implementation in our [pinned parameter audit](feedback-parameters.md#denoise-and-steps-are-different-controls). The model-ranking discussion dates itself to the recording and is not a 2026 recommendation.

**For our loop:** useful foundation for reading graphs and debugging missing pieces, with little new animation-specific evidence. “Update all” is an installation tutorial shortcut, not a way to preserve our archived experiment runtime. The transcript also discloses a hosted-service affiliate link; current descriptions are mutable and advertise a different service.

### V08 — 10 essential ComfyUI nodes

[Sebastian Kamph · 2026-02-20 · 22:45](https://www.youtube.com/watch?v=rVj_rSSvPjs)

- **01:20–04:55:** VHS frame metadata, caps, skipped frames and every-nth sampling.
- **11:00–14:20:** VAE/text/latent roles; recoloring a node does not change positive/negative wiring.
- **14:40–16:40:** KJ resize choices, aspect ratio and size outputs.
- **16:40–21:00:** Shared primitive controls, notes, text previews and Set/Get references.

**Artifact check:** [VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite) documents the frame-selection behavior; [KJNodes](https://github.com/kijai/ComfyUI-KJNodes) is the named resize package. This validates node families, not every UI label/version or performance claim.

**For our loop:** frame count/rate metadata and intermediate previews make animation graphs easier to inspect. They do not create temporal coherence. A preview of an upstream prompt alone would not reveal conditioning that Difforum evaluates internally for each frame. Avoid interpreting the video's “steps like frames” analogy as generated-video frames.

### V09 — ComfyUI KSampler Explained: Samplers, Steps, CFG, Seed & Denoise

[Floyo AI, created with Sebastian Kamph · 2026-05-24 · 10:14](https://www.youtube.com/watch?v=v88YOP3DdTw)

- **01:30–03:29:** Seed and post-generation seed controls.
- **03:29–05:53:** Steps and CFG, with model-dependent recommendations.
- **05:53–07:59:** Sampler/scheduler distinction.
- **07:59–10:10:** Denoise ranges and strong endpoint claims.

**Validation:** Useful vocabulary, but “same image every time” omits runtime reproducibility limits. Zero denoise is not a pixel-preserving bypass of our warp/effects/VAE/color chain. Denoise one also cannot remove independent ControlNet/IPAdapter conditioning. See [our parameter audit](feedback-parameters.md).

**For our loop:** a recent source to read critically, not a prescription to lower denoise to a generic 0.5–0.7 range. The description advertises a sampler comparison, while the retrieved narration mostly provides conceptual explanations; no visual benchmark was examined. Count this together with V07/V08 as the same author's teaching, not three independent confirmations.

### V10 — Smooth 48 FPS Video with RIFE Frame Interpolation

[Olares × SweetValberry · 2026-05-14 · 03:28](https://www.youtube.com/watch?v=LHunwnT2afc)

- **00:08–01:30:** Loads a Wan clip as frames and adds RIFE VFI.
- **01:30–02:16:** Multiplier 3, 16→48 FPS, matching video-combine rate; mentions cache/ensemble memory controls.
- **02:16–02:45:** Subsamples the interpolated result for a lower delivery rate.

**Artifact check:** [ComfyUI-Frame-Interpolation](https://github.com/Fannovel16/ComfyUI-Frame-Interpolation) implements RIFE over image pairs. Its retrieved node code adds intermediates between originals; the method can therefore consume image-loop outputs too.

**For our loop:** use original distinct PNGs, not the already repeated 24-FPS export. Preserve the raw clip and inspect contours, occlusions and texture in an interpolated comparison. The author's smoothness statement is an example-specific assertion. Their broad 16-FPS Wan wording and “any target rate” shortcut are not universal model or timing rules; verify actual input timestamps and final duration.

### V11 — Using Latent Blends in ComfyUI

[Rob Adams · 2025-11-03 · 08:58](https://www.youtube.com/watch?v=g1X7YMr4Kmg)

- **01:40–03:30:** Mixes two encoded images before further denoising; one provides a contrasting style/texture.
- **04:30–06:25:** Changing blend amount can introduce style, swamp the original, or allow its figure to reappear.
- **06:25–08:35:** More exploratory references and refinement, without a temporal sequence.

**Artifact check:** The [shared Drive workflow](https://drive.google.com/file/d/1g1mIcBbGALKwl8j322OszzgMPxqtL277/view) downloaded as a 62-node JSON. It contains core `LatentBlend` with value 0.5 and explicitly loads `flux1CompactCLIPAnd_Flux1DevFp8.safetensors`; it is not an SDXL experiment. Node provenance records several historical Comfy versions.

**For our loop:** explicit latent blending is a distinct possible input operation. It must not be confused with denoise, previous-image retention, pixel blending or time interpolation. The author's stronger claims about preferable blends and broad model support are untested here. A smooth parameter sweep would still not guarantee a smooth semantic morph.

### Selected but unavailable — prompt scheduling

[CG TOP TIPS · ComfyUI Basic - Txt2Vid with Prompt Scheduling · 2024-05-25 · 13:12](https://www.youtube.com/watch?v=C14wRsJ7qBo)

The description names Batch Prompt Schedule, empty batched latents and FILM. Transcript API attempts reported `TranscriptsDisabled`; yt-dlp reported `CaptionMissing`; the final supported OpenAI audio attempt returned `OpenAITranscriptEmpty` for the first audio chunk. The empty text does **not** prove the video is silent. No speech-derived conclusions or timestamps are claimed.

The separate [FizzNodes author documentation](https://github.com/FizzleDorf/ComfyUI_FizzNodes/wiki/Prompt-Schedules) does establish scheduled text/value interpolation, common text via `pre_text`/`app_text`, and distinct per-frame versus batched interfaces. Batch length must match the batched conditioning. It does not establish that this tutorial produces recurrent feedback, or that FizzNodes is needed when Difforum already evaluates its own schedule.

## Contradictions and compatibility traps

| Tempting interpretation | What the evidence actually permits |
| --- | --- |
| “Denoise 0.5 keeps half the previous picture.” | V07 uses that metaphor. Our pinned sampler selects part of a sigma schedule; it does not perform a 50/50 pixel mix. |
| “Same seed means the same movie.” | Same seeded inputs help comparisons. Version/backend differences, state and repeated feedback still matter. Neither tutorial nor this study measured complete render determinism. |
| “Increment seed is a smooth noise trajectory.” | Incrementing indexes another pseudorandom field. V03's explicit blending of noise fields is a different operation. Its animation benefit remains untested. |
| “More steps fixes detail; Lightning's settings are faster equivalents.” | V05 uses a distilled checkpoint; our SDXL base uses a different regime. V02 values fine denoise control. P04's local speed/visual result remains stronger evidence for this artwork than generic advice. |
| “A frame batch or auto-queue is a feedback loop.” | V04's temporal model, Fizz batched prompts, V05's historical graph state and our internal recurrent sampler are different execution mechanisms. Follow the image dependency, not the word animation. |
| “ControlNet keyframes always mean movie-frame keyframes.” | [Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet#scheduling-explanation) distinguishes denoising-timestep keyframes from latent/batch-index keyframes. V06 uses the former. |
| “A 24-FPS export has 24 motion samples each second.” | VHS can repeat/drop frames or change playback rate. RIFE predicts intermediate images. Our repeated export adds no new image states. |
| “ControlNet makes detail better.” | Guides constrain structure. A sparse hint can compete with ornament; V02 adjusts guide strength/timing and references. Removing guidance also does not remove previous-image feedback. |
| “Reference style has no content.” | V02 describes unwanted subject leakage. Style/composition separation is useful, not perfect disentanglement. |
| “A current tutorial's default nodes and values fit our runtime.” | The actual downloaded graphs identify older node versions and different checkpoints. They were inspected, not imported or executed on ComfyUI 0.34.0. |

There are also **four different things called interpolation** in these sources: prompt/value interpolation across movie time; reference-mask or latent blending; conditioning schedules inside one sampling pass; and synthesis of output frames between completed images. Keep those timelines explicit when proposing a workflow.

One small but concrete timing trap came from validating V10. In the [retrieved RIFE node](https://github.com/Fannovel16/ComfyUI-Frame-Interpolation/blob/main/vfi_models/rife/__init__.py), without skipped pairs and with constant multiplier `m`, output count is `(N−1)×m+1`. Thus 48 inputs with multiplier 3 produce **142 images**, not automatically a 144-image, six-second 24-FPS export. This is source inspection of the retrieved version, not installed-version verification. Endpoint policy must be explicit; do not silently shorten a comparison.

## What remains useful as tutorials age

**Durable:** inspect the intermediate representation; distinguish reference style from structure; align prompt/mask/image counts; match encoded images and their model/VAE; treat seeds and noise separately; preserve source frames; use explicit timelines; expect reference-specific tuning; compare authored artifacts with narrated claims.

**Dated or conditional:** exact Manager buttons, node IDs, model filenames, preferred checkpoints, sampler defaults, arbitrary denoise ranges, “best” IPAdapter variants, 16-frame AnimateDiff advice, and hardware/performance claims. The [IPAdapter repository](https://github.com/cubiq/ComfyUI_IPAdapter_plus) has a **2025-04-14 maintenance-only notice**. Its conceptual value persists, but it is not evidence of active 2026 feature development or compatibility with every current model.

**Relevant nodes to understand, not an install list:** IPAdapter style/composition and masks; ControlNet preprocessing and timestep controls; Fizz prompt/value scheduling; explicit noise/latent mixing; VHS frame I/O; RIFE/FILM after generation; KJ resize helpers. Many concerns already have working equivalents in this repository. None of these node families, by itself, supplies a validated improvement to the current artistic result.

## Proposed next comparisons

These are research deductions, not implemented changes or an approved architecture. The [architecture comparison](deforum-architecture-comparison.md) provides the combined execution proposal:

1. **Separate presentation smoothness from morph quality.** Compare a preserved P01/P03/P04 source sequence against a correctly timed interpolation export. This isolates repeated-frame judder while leaving semantic endpoints unchanged. Success means visibly better continuity without distracting outline/texture artifacts; smoother playback alone does not rescue wrong transformations.
2. **Direct one transformation while retaining the art vocabulary.** Retain shared surface, lighting and composition language while changing a specific subject across a few planned states. Judge sustained morphing and detail together against a preferred clip; P06 remains the constant-prompt control. Fizz's shared-text pattern is an authoring idea, not a requirement to replace Difforum scheduling.
3. **Only if wording is insufficient, compare a sparse visual handoff.** A style anchor plus evolving subject/region references is supported as a technique by V01/V02/V04. Whether the existing sampler can evaluate it properly belongs to the source audit. Added conditioning must earn its place by improving the preferred motion, not merely freezing recognizable objects.
4. **Consider correlated noise or explicit latent mixing only as distinct experiments.** V03/V11 supply mechanisms, not evidence of success in this loop. Neither should be hidden inside another settings change or treated as equivalent to lowering denoise.

This ordering does not select a new model or native-video architecture. The most defensible conclusion is that the corpus offers **control mechanisms and diagnostic distinctions**, while the reference match still needs a short, judged experiment on our own artwork.

## Reusable corpus and artifact inventory

All raw captions, downloaded author assets and intermediate research files are ignored locally under:

```text
/Users/olof/git/ai-video-experiments/apps/deforum/work/deforum-architecture-research/youtube/
```

| Relative path in that directory | Contents |
| --- | --- |
| `queries.txt`, `focused-queries.txt` | Exact query sets. |
| `search-receipt.json`, `focused-search-receipt.json` | Skill run IDs and original corpus paths. |
| `search/meta.json`, `search/videos.jsonl` | First-pass metadata and normalized results. |
| `focused-search/meta.json`, `focused-search/videos.jsonl` | Follow-up metadata and normalized results. |
| `candidates.jsonl` | 69 deduplicated search candidates, metadata only. |
| `selected-ids.txt` | The 12 enrichment selections. |
| `videos/VIDEO_ID.json` | Original single-video skill response; record is under `result`, transcript under `result.transcript`. Includes description, metadata and provider attempts. |
| `transcripts/VIDEO_ID.txt` | Full recovered text for each of the 11 successful videos. |
| `transcripts/VIDEO_ID.timed.jsonl` | Original timestamp/duration/text snippets. |
| `selected-manifest.json` | Titles, dates, durations, status, provider attempts, paths, text SHA-256, snippet counts and final caption offsets. |
| `enriched-corpus.jsonl` | 70 normalized video records, including selected transcripts and the additional author-linked video. |
| `coverage.json` | Machine-readable actual scope and totals. |
| `enrichment-progress.jsonl` | Exit codes and elapsed retrieval times; projection corrected to the skill's nested response shape. |
| `sources/manifest.json` | Exact source URLs, retrieval times, local paths, sizes and SHA-256 for downloaded sources. |
| `sources/latent-style-workflows.zip`, `sources/style-workflows/*.json` | Author's intact ZIP and its four extracted workflow JSONs. |
| `sources/mick-sdxl-workflow.txt`, `sources/rob-latent-workflow.txt` | Downloaded workflow JSONs, despite the archive's `.txt` filename suffix. |
| `sources/ipadapter-*`, `sources/fizz-*`, `sources/noise-*`, `sources/rife-*`, `sources/acn-readme.txt`, `sources/vhs-readme.txt`, `sources/kj-readme.txt` | Supporting upstream docs/code and example snapshots; retrieval is not runtime verification. |
| `enrich.py`, `archive-sources.py`, `finalize-corpus.py` | Local orchestration around the existing skill and archive normalization; not a new installed tool or application workflow. |

Original skill search locations:

```text
/Users/olof/git/codex-config/tmp/youtube-video-research/20260907T091526Z-comfyui-recurrent-surreal-morphing-m-2b162f04a31e/
/Users/olof/git/codex-config/tmp/youtube-video-research/20260907T091559Z-comfyui-specialist-foundations-and-r-4d06cc7f0acd/
```

The main first-pass filters were `--published-after 2025-01-01T00:00:00Z --published-before 2026-09-08T00:00:00Z --relevance-language en --comments 0 --no-transcript`. The upper bound was tomorrow midnight relative to retrieval; no future unpublished video is implied. The follow-up omitted the lower publication bound. Both used `corpus-search`, `--per-query-max-results 5`, `--shortlist-size 12`, relevance ordering and `--save-only`; the automatically ranked shortlist was replaced by the explicit research selections.

Enrichment used the existing skill command through its authorized shared environment, with three concurrent video retrievals:

```text
/Users/olof/git/codex-config/scripts/codex-uv-run \
  /Users/olof/git/codex-config/skills/custom/youtube-video-research/scripts/youtube_video_data.py \
  video --video VIDEO_ID --comments 0 --transcript-max-chars 0 --transcript-format both
```

`--transcript-max-chars 0` disables character truncation. Saved output is reusable without network access. Do not rerun the enrichment driver merely to inspect results: it performs retrieval again and may reach a paid audio fallback. Do not add the ignored corpus, transcripts or author media to public Git; this report contains original summaries and links rather than redistributed full transcripts.

## Evidence limits and blockers

- **No videos watched or generated:** transcripts were read in full, with timestamps retained; author JSONs/docs were inspected. Screen-only values, demonstration quality, editing omissions and actual motion remain unverified.
- All 11 successes used **yt-dlp captions** after transcript-API `RetryError`. The normalized records identify language `en-orig` but do not reliably identify manual versus automatic origin; misrecognized names/numbers are visible in the text. No claim of human-verified captions is made.
- The single unavailable scheduling video exhausted the supported caption and audio routes. Its final OpenAI attempt returned empty text; paid fallback usage/cost was not measured. It is excluded from transcript-derived coverage.
- Web extraction initially failed for the ZIP, Drive file and Patreon attachment. Ordinary direct retrieval of the authors' public download links succeeded; both shared JSONs parsed, and the ZIP passed integrity validation. No account login or paid advanced-workflow access was used.
- Author artifacts corroborate topology and intended operation, **not current executable compatibility or measured output quality**. Some graph versions differ across nodes, and historical titles/descriptions can change independently of upload dates.
- No comments were used. Six editorial source groups account for the 11 transcripts when the Kamph/Floyo overlap is collapsed; this is not eleven independent confirmations. Strong direct evidence for modern recurrent SDXL morphing remains sparse.
- Only this report and the ignored YouTube research directory were authored. No shared index, AGENTS file, learning journal, GPU resource, production workflow, commit or push was changed by this sidecar.
