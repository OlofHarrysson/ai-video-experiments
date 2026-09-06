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
- Seedream was tested as a still-image source. Its image has not yet been animated in this project; liking that still does not establish a video-quality preference.
- Olof's preferred amount of morphing, camera speed and clip duration for this scene remain open. Parameter names shown in reports are not evidence of familiarity with those controls.

## Next learning opportunity

Proposed: start from the preferred Seedream image and show two three-second videos with the same gentle 3D camera path: recurring SDXL feedback and independent guide redraw. Give each its own large preview in chat. Longer equal-duration clips should be easier to compare than the previous one-second redraw sample.

The useful creative question is which balance of preserved scene structure and visible transformation Olof prefers. The technical question is whether SDXL repainting retains enough of the Seedream look. This is a workflow comparison, not a test of animating natively with Seedream. Record the actual feedback afterward; until then, the preference is unconfirmed.
