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
| Show videos directly in chat with a short experiment summary. Reports are supporting material. | “I'm mostly interested in seeing the video outputs and maybe with a brief summary of the experiment.” | Embed playable local videos in the final response, label each with what changed, and give one or two sentences about the result. A report link alone is insufficient. |
| The Seedream marsh image is the preferred look among the displayed samples. | “I like the sea dream one.” | Use that image as the candidate reference for the next animation comparison. This does not establish a preference for every Seedream model or for videos generated with it. |
| More visible movement than the first short clips. | On 2026-09-07: “what I see right now is a little bit too static”; Olof suggested short duration might contribute. | Test longer clips with clearer camera travel. Desired motion amount remains unconfirmed. |
| Learn by trying several workflows and inspecting each result. | On 2026-09-07 Olof authorized ten experiments, chosen one or two at a time, with useful independent work in parallel. | Let observed results determine the next tests; show every video and highlight the useful findings. |
| Give the assistant a local way to inspect videos over time. | “extract frames at specific timestamps or events” to understand roughly what happens. | Preserve timestamped frame reviews and use them before describing a clip; distinguish sampled-frame evidence from full playback and semantic understanding. |
| Do not assume all assistant output is read. | “I often read all of the output, but not always, and sometimes I only read half.” | Surface the result and the one useful next decision. Avoid building explanations on assumed familiarity with reports. |
| Prioritize an iterative filmmaking workflow and intentional 3D camera movement. | Olof described keeping good openings, restarting from a chosen frame, and assembling longer films from shorter clips; explicitly preferred 3D camera work. | Preserve originals and branches; practice short, inspectable continuations before extending duration. |
| Find a balance between smoothing and flicker. | Earlier playback feedback: the lower-denoise version was too smooth and the higher-denoise version flickered too much. | Treat this as feedback on those clips. Keep detail, morphing and temporal variation separate; do not declare a universally preferred denoise value. |

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

- The [parallel experiment results](research/parallel-experiments-session.md) were shared. Do not assume the reports were read.
- SDXL feedback and independent-redraw videos were embedded in chat. Olof has not yet stated a playback preference between these workflows.
- We explained that cropping reduced raw uncovered guide pixels but left interior gaps. No user explanation or assessment of this result has been recorded.
- Seedream was tested as a still-image source. Its image has now been animated with SDXL in the Seedream motion study; both five-second videos were surfaced in chat. No preference between those completed outputs is recorded.
- Olof's preferred amount of morphing, camera speed and clip duration for this scene remain open. Parameter names shown in reports are not evidence of familiarity with those controls.

## Camera craft interest — 2026-09-07

**Explicit:** Olof asked for research on classic camera moves, then expanded the scope to directing, cinematography, visual storytelling and film creation. He prioritizes image-led storytelling, with music possible later and little current need for dialogue or screenplay writing. He said he would like to learn about cinematography and have the research saved as a document after this render task.

**Demonstrated hypothesis:** Olof connected nearby foreground objects with making 3D movement visible, and noted that rotating a camera can move the subject out of frame. This is useful reasoning to explore; it does not yet establish the distinction between translational parallax and rotation, or knowledge of shot terminology.

## Next learning opportunity

Completed on 2026-09-07: [ten adaptive video experiments](research/ten-experiments-session.md), including the first three-shot story, five camera/settings comparisons, native Seedream frame edits and three independent-redraw workflows. Each has a playable video and timestamped review. The story also has a shorter revised cut selected from the earlier, clearer source ranges. No user playback verdict on this round has been recorded.

The useful creative question remains the balance of preserved scene structure and visible transformation. E09 is an assistant-selected candidate for preserving structure; E10's accidental lantern transformation may suit surreal animation. E07 now establishes native Seedream editing of successive guide frames, with variable canvas borders. Show these differences without assuming which tradeoff Olof prefers.

The [filmmaking research guide](research/filmmaking-for-ai-animation.md) remains available. E01 applies its three-state story exercise; neither creating that cut nor presenting the guide establishes Olof's understanding of film craft.
