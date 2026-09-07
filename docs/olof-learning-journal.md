# Olof's learning journal

Living notes about creative preferences and learning in this project. Started 2026-09-07. This is a record of evidence from conversation, not an assessment of general ability or a transcript of everything presented.

## How to maintain this journal

- **Explicit:** Olof directly stated a preference, intention or prior experience. Keep its original scope.
- **Demonstrated:** Olof explained a concept or used it to propose something. Record what that demonstrates without inferring implementation skill or broader mastery.
- **Unconfirmed:** We presented a result or explanation, or have a tentative interpretation. Presentation, silence and a brief acknowledgment do not establish that it was read, watched, understood or retained.
- Date additions and include a short quote or concrete conversational evidence. Use links to experiment reports for technical detail.
- Update when natural conversation supplies evidence. Ask a short question when it helps the next creative decision; do not turn ordinary collaboration into a quiz.
- Keep current preferences easy to find. When a preference changes, briefly preserve the earlier context rather than treating either preference as universal.
- Keep notes specific to this project. Do not infer personal traits or copy unrelated profile information here.

## Current preferences — explicit

Recorded 2026-09-07 from this project's conversation.

| Preference | Evidence | How to respond |
| --- | --- | --- |
| Show a small, understandable shortlist of videos directly in chat. Reports support it. | Initially: “I'm mostly interested in seeing the video outputs.” Later on 2026-09-07, Olof found six similar results overwhelming and asked for assistant screening and clearer explanations. | Default to one recommendation and one meaningful alternative, with what changed, why, what to watch and the result. Keep all outputs indexed. Explain unfamiliar tools; labels alone do not support useful feedback. |
| The Seedream marsh image is the preferred look among the displayed samples. | “I like the sea dream one.” | Use that image as the candidate reference for the next animation comparison. This does not establish a preference for every Seedream model or for videos generated with it. |
| Existing artwork should set the next visual benchmark. | On 2026-09-07 Olof supplied Tomorrow.mov and Brain Entity, identified both as Deforum work, and said “this style that we have right now is not good enough.” | Study and reproduce a short segment's visual qualities before further broad parameter sweeps. Models/settings may differ. These two references are explicitly liked; the specific reasons for liking each remain our interpretation. |
| Brain Entity v002 is closer to the intended direction, but not yet good enough. | On 2026-09-07: “Version two is much closer to what I had in mind, but it is not great.” | Use v002 as the comparison baseline. The particular qualities Olof prefers and dislikes remain unconfirmed; do not equate this with approval of stronger denoise, flicker or simplified shapes. |
| More visible movement than the first short clips. | On 2026-09-07: “what I see right now is a little bit too static”; Olof suggested short duration might contribute. | Test longer clips with clearer camera travel. Desired motion amount remains unconfirmed. |
| Setup latency matters during creative iteration. | During the Brain Entity study on 2026-09-07, Olof asked why setup was slow and said “I find it a bit annoying.” | Separate new-image build time, worker cold start and warm inference. Reuse a prepared model/tool package and warm workers within a bounded session; avoid presenting serverless as inherently fast. |
| Learn parameter effects through controlled, artwork-specific experiments. | On 2026-09-07 Olof emphasized guidance, previous-image blending, denoising steps and added noise, and said results differ by model, prompt and artwork. | Treat settings as hypotheses. Separate what the node code does from what a rendered comparison shows; preserve matched conditions and avoid universal best-setting claims. |
| Start from proven examples and make small departures while learning. | On 2026-09-07: “stick a little bit to the templates and then do small excursions out from that to learn something new.” Olof authorized the assistant to choose the most important research-informed tests and noted that accomplished artists may have spent hundreds of hours iterating. | Reuse documented mechanisms, isolate changes and judge short experiments by what improves and what they teach. Do not equate agreement with the research plan with understanding every mechanism or approving new videos. |
| Learn by trying several workflows and inspecting each result. | On 2026-09-07 Olof authorized ten experiments, chosen one or two at a time, with useful independent work in parallel. | Let observed results determine the next tests; show every video and highlight the useful findings. |
| Give the assistant a local way to inspect videos over time. | “extract frames at specific timestamps or events” to understand roughly what happens. | Preserve timestamped frame reviews and use them before describing a clip; distinguish sampled-frame evidence from full playback and semantic understanding. |
| Do not assume all assistant output is read. | “I often read all of the output, but not always, and sometimes I only read half.” | Surface the result and the one useful next decision. Avoid building explanations on assumed familiarity with reports. |
| Prioritize an iterative filmmaking workflow and intentional 3D camera movement. | Olof described keeping good openings, restarting from a chosen frame, and assembling longer films from shorter clips; explicitly preferred 3D camera work. | Preserve originals and branches; practice short, inspectable continuations before extending duration. |
| Find a balance between smoothing and flicker. | Earlier playback feedback: the lower-denoise version was too smooth and the higher-denoise version flickered too much. | Treat this as feedback on those clips. Keep detail, morphing and temporal variation separate; do not declare a universally preferred denoise value. |

## Parameter-study playback feedback — 2026-09-07

**Explicit:** Olof likes this round substantially more than the preceding videos. P06 has good clarity but feels like a sequence of stills with insufficient temporal consistency; it is not the preferred motion baseline. P01 has interesting morphing and better continuity, but changes should unfold through more intermediate frames instead of abrupt complete redraws. P02 begins well and becomes boring late. P03 is “really good,” with a flatter ending. “Before is also really cool” is interpreted as P04 from the sequence of comments, with that reference slightly uncertain. P05 also looks good and shares the abrupt-change problem.

**Next priority:** apply the completed architecture and tutorial research in [continuity experiments](../apps/deforum/projects/brain-entity-study/experiments/continuity.md). Preserve surreal semantic morphing while making its transitions more gradual. The claim that architecture or workflow is contributing is a user hypothesis to investigate, not an established diagnosis. Detailed still frames alone are insufficient for selecting a preferred video.

## Continuity review and collaboration feedback — 2026-09-07

**Explicit:** C01/C03 were “a bit boring”; the other outputs were “pretty good.” Olof tentatively prefers **P3 + RIFE**, but says the differences are difficult to judge. This supersedes the assistant's C02 + RIFE recommendation. Do not strengthen this into a definitive ranking of every clip.

**Explicit working preference:** the assistant should inspect many useful images selectively, starting with evenly spaced samples and then every frame in selected intervals. Olof wants the assistant to screen results and surface important differences, reducing the need to hold many similar clips in mind. Keep videos inline and explain what the viewer is seeing; terms such as “Flow Stabilize” were unclear. When a video is liked, explain its important ingredients.

**Explicit project purpose:** learning the industry and tools, improving the collaboration, and improving the videos are all part of this work. Olof asked to keep the process in repository instructions as a living agreement. See [reviewing experiments together](review-and-feedback.md).

**Unconfirmed:** the new explanation of RIFE, flow stabilization, fixed seeds and controlled comparisons has been presented. No understanding or retention is inferred from that. The new harness and shortlist convention also need experience and feedback before treating them as proven improvements.

## Current baseline and new references — 2026-09-07

**Explicit:** Olof calls the current P3 + RIFE result “pretty good” and says “the morphing is nice,” while its camera movement is not very interesting. Keep it as the creative baseline and investigate more purposeful camera work. He would prefer a newer model eventually, but explicitly accepts continuing with SDXL now that a recipe is working.

**Explicit:** Olof supplied [Frustration and Intoxication](../apps/deforum/projects/reference-studies/references/bonsai-frustration-and-intoxication.md) and [SDXL motion-preset examples](../apps/deforum/projects/reference-studies/references/bonsai-motion-presets.md), both by The BonsAi Effect, as high-quality references. He asked for visual review and research across descriptions, comments and other platforms. The second link starts at 9:25 inside Evolve Zoom Slow; this timestamp is a useful study target, not an explicit ranking of all presets.

**Unconfirmed:** the [channel study](research/bonsai-effect-workflow.md) documents hybrid motion, seed mixtures, cadence, strength translation and editing. Presenting this research does not establish that Olof understands or prefers those mechanisms. We have not reproduced the newly supplied references or selected an implementation path for their presets.

**Explicit follow-up:** Olof asked what “takes motion from an expanding white ring on black” means and said the earlier discovery explanation was unclear. He accepted an 8–10-second slow-zoom reference test, while stressing that we should move quickly into the reference's 3D transformations. Do not make a broad zoom-parameter sweep a prerequisite. The actual guide and a step-by-step explanation were presented; understanding remains unconfirmed. See the [two-test brief](../apps/deforum/projects/reference-studies/experiments/bonsai-motion.md).

**Further clarification:** Olof reports understanding diffusion/denoising, but still wants to understand how the ring influences the output. Explain the ordinary pixel warp before VAE encoding and img2img, including why changing that starting image influences denoising; distinguish it from an inpainting mask or model weights. He prefers keeping ComfyUI as the main platform. An isolated original-Deforum RunPod test is acceptable if easy or substantially useful, but he does not want a large investment in another platform and explicitly asked to align before proceeding. This is conditional permission, not evidence that setup is easy or that a migration is wanted.

**Visual examples requested:** Olof says he “sort of” understands vector-field distortion and describes needing two guide frames to estimate movements applied to an artwork. This demonstrates the two-frame-to-motion relationship, not complete understanding of flow estimation or warping. He asked to see the guide frames, intermediate deformation and next artwork, and explicitly chose to continue with ComfyUI while deferring A1111/Forge. After the [interactive walkthrough](../apps/deforum/projects/motion-guide-study/README.md), he reports partial understanding, still finds it somewhat difficult, and wants to move on; do not infer full understanding or prolong the explanation without a new question.

**Walkthrough aesthetic feedback (2026-09-07):** Olof calls the SDXL repaint “horrific” and says it looks like a completely new picture. It is acceptable as a mechanism demonstration, but unacceptable as a single animation step. He wants gradual changes across multiple frames, possibly affecting only parts of the image. Preserve this feedback separately from his positive judgment of the earlier P3 + RIFE animation; neither result establishes a universal denoise setting or verdict on SDXL.

**Model continuity priority (2026-09-07):** Olof explicitly wants to investigate using the same model for the initial image and every subsequent frame before tuning other settings. He explains that the same prompt can produce different images across models or seeds, and hypothesizes that a fixed seed may also be necessary. This demonstrates awareness of model/seed effects on image generation; it does not establish that seed changes necessarily break img2img continuity. Source inspection confirms Deforum supports both fixed and changing seeds. Keep one exact model recipe and fixed seed as the next diagnostic baseline; do not record cross-model animation as universally impossible.

**Matched seed experiment requested (2026-09-07):** Olof explicitly asks for two experiments sharing the starting seed, with one holding it fixed and the other changing it from the second frame onward. The [completed comparison](../apps/deforum/projects/motion-guide-study/experiments/seed-comparison.md) uses identical opening pixels and otherwise matched settings. Assistant review favors the changing-seed branch; Olof's preference and interpretation of these new results are unconfirmed. Do not turn the assistant's findings into a claim that Olof now understands or prefers a particular seed policy.

**Seed comparison playback feedback (2026-09-07):** Olof rejects A's fixed-seed result and explicitly selects B for a small 3D camera experiment. He accepts random or whichever changing-seed implementation is simplest. Keep B's incrementing seeds for simplicity and reproducibility. This supersedes the pending preference above; it does not establish that fixed seeds fail for all recipes or that Olof endorses every detail of B's output. [3D follow-up](../apps/deforum/projects/motion-guide-study/experiments/seed-3d.md).

## Spatial motion clarification — 2026-09-07

**Explicit playback feedback:** Olof could barely perceive camera motion in B's 3D repaint. He saw movement in the depth-only preview, but wanted a more dramatic effect. This supersedes the pending feedback in the original experiment report.

**Explicit creative interest:** the supplied BonsAi Effect films, *Child of the Moon* and *Echoes of a Thousand Years*, join the preset compilation as desired art/production references. Olof notices different regions moving in different directions and questions whether literal 3D camera movement is the right objective. Prioritize expressive spatial motion; do not interpret this as rejecting every 3D method.

**Demonstrated hypothesis, partial understanding:** Olof describes moving/stretching regions over successive frames and combining this with pan, zoom and rotation. He explicitly says the vector-field concept is not fully clear. Explain translation versus differential stretching, newly exposed pixels, and how depth/camera projection can also produce 2D displacements. Do not infer that the references use a particular method from appearance alone.

See [spatial motion and the new references](research/bonsai-spatial-motion.md). The subsequent acceptance and completed regional-flow experiment are recorded below.

**Research priority:** Olof explicitly identifies Safety Marc's preset repository as important evidence of successful spatial image controls. Study the effects through their settings, actual guide footage and underlying implementation before inventing new controls. He expects concrete explanations of how the demonstrated effects work.

**Accepted experiment:** Olof agrees to the short Move-Warp-inspired test. He also clarifies that in the referenced movement, the left/right regions did not move vertically as expected from a simple global rotation. That observation strengthens his regional-deformation hypothesis; it does not identify the exact algorithm. The [experiment](../apps/deforum/projects/motion-guide-study/experiments/move-warp.md) uses the actual wave guide with B's repaint recipe.

**Explicit Move-Warp playback feedback:** Olof says the result looks much better and the movement makes it more interesting. He cannot yet judge whether it is the right movement. He noticed the whole image shifting right and asked whether panning was also applied. The saved flow has a net rightward displacement; there was no separate pan. Understanding of this distinction remains unconfirmed.

## Concepts demonstrated in conversation

Recorded 2026-09-07; these observations describe specific explanations or suggestions, not a level of expertise.

| Concept | Evidence | Supported conclusion and limit |
| --- | --- | --- |
| Image feedback animation | Olof described altering the camera, rendering another image and feeding images through the sequence. | Recognizes the basic recurring image-generation loop. Particular node behavior and parameter effects remain unconfirmed. |
| Overscan and delivery crop | Olof proposed “generating a bigger kind of viewport than what we show to the user” to address edges. | Independently proposed extra image margins as a possible technique. This does not establish understanding of interior disocclusion or agreement with our measured result. |
| Non-destructive iteration | Olof described keeping all generations, selecting the best clips, and continuing from a point that still works. | Articulated an editing and preservation model. Ability to operate the current CLI has not been assessed. |
| Structure versus style | Olof distinguished recognizable objects, contours and camera movement from patterns/textures, while noting the concepts can overlap. Also reported having used style transfer before. | Has a useful conceptual framing and self-reported prior experience. Current model controls and their limitations are separate learning questions. |

## Presented but not confirmed

As of 2026-09-07:

- The [continuity study](../apps/deforum/projects/brain-entity-study/experiments/continuity.md) has now received playback feedback: P3 + RIFE is the tentative favorite, and C01/C03 were boring. Understanding of the mechanisms remains unconfirmed; see the dated feedback above.
- Six [Brain Entity parameter comparisons](../apps/deforum/projects/brain-entity-study/experiments/parameters.md) were rendered with isolated changes to guide strength, denoise, CFG, steps, noise and prompt travel. Olof subsequently assessed these clips: P06 is clear but lacks temporal continuity; see playback feedback above. The parameter research explains this node’s behavior, but reading or understanding it is unconfirmed.
- The [parallel experiment results](research/parallel-experiments-session.md) were shared. Do not assume the reports were read.
- SDXL feedback and independent-redraw videos were embedded in chat. Olof has not yet stated a playback preference between these workflows.
- We explained that cropping reduced raw uncovered guide pixels but left interior gaps. No user explanation or assessment of this result has been recorded.
- Seedream was tested as a still-image source. Its image has now been animated with SDXL in the Seedream motion study; both five-second videos were surfaced in chat. No preference between those completed outputs is recorded.
- Olof's preferred amount of morphing, camera speed and clip duration for this scene remain open. Parameter names shown in reports are not evidence of familiarity with those controls.

## Camera craft interest — 2026-09-07

**Explicit:** Olof asked for research on classic camera moves, then expanded the scope to directing, cinematography, visual storytelling and film creation. He prioritizes image-led storytelling, with music possible later and little current need for dialogue or screenplay writing. He said he would like to learn about cinematography and have the research saved as a document after this render task.

**Demonstrated hypothesis:** Olof connected nearby foreground objects with making 3D movement visible, and noted that rotating a camera can move the subject out of frame. This is useful reasoning to explore; it does not yet establish the distinction between translational parallax and rotation, or knowledge of shot terminology.

## Next learning opportunity

Current preparation: use the [BonsAi Effect study](research/bonsai-effect-workflow.md) to ground the next camera/morphing experiment in an existing preset. Preserve P3 + RIFE for comparison. The useful lesson to explain is the distinction between guiding motion before repainting and creating intermediate frames afterward; understanding remains unconfirmed.

Earlier direction: [Brain Entity style study](../apps/deforum/projects/brain-entity-study/README.md), following the [reference studies](../apps/deforum/projects/reference-studies/README.md). On 2026-09-07 Olof accepted the proposed six-second Brain Entity-inspired test with “let's try to do that.” Its creator credits SDXL/art LoRA/QR ControlNet; Tomorrow's Deforum attribution comes from Olof. Neither reference's exact settings are established.

Completed on 2026-09-07: [ten adaptive video experiments](research/ten-experiments-session.md), including the first three-shot story, five camera/settings comparisons, native Seedream frame edits and three independent-redraw workflows. Each has a playable video and timestamped review. The story also has a shorter revised cut selected from the earlier, clearer source ranges. No user playback verdict on this round has been recorded.

The useful creative question remains the balance of preserved scene structure and visible transformation. E09 is an assistant-selected candidate for preserving structure; E10's accidental lantern transformation may suit surreal animation. E07 now establishes native Seedream editing of successive guide frames, with variable canvas borders. Show these differences without assuming which tradeoff Olof prefers.

The [filmmaking research guide](research/filmmaking-for-ai-animation.md) remains available. E01 applies its three-state story exercise; neither creating that cut nor presenting the guide establishes Olof's understanding of film craft.

## Motion vocabulary practice — 2026-09-07

**Explicit direction:** Olof wants a few distinct effects drawn from Safety Marc's presets, including a 3D rotation-like effect. The learning objective is to connect everyday descriptions to mathematical controls and visible outputs. He does not yet regard the wave guide's strong rightward estimate as intuitively explained. Prioritize examples and preserve the chain from guide or camera settings through warped input to repaint. Independent invention of a broad motion-control system can come later.

## Spatial effects playback feedback — 2026-09-07

**Explicit preference:** radial unfolding is by far Olof's favorite of the three spatial effects. He wants more effect trials and stronger/exaggerated movement, particularly for the ring. He finds the turn/bank motion useful for repositioning the figure, despite disliking the large black empty region.

**User hypothesis:** more noise might help fill the black region. This is a proposed explanation to test, not a demonstrated understanding of warp coverage or a proven remedy. Preserve useful motion while investigating missing-content handling.
