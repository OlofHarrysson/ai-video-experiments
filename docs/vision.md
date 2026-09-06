# Iterative filmmaking

Living direction, recorded 2026-09-06 from Olof's brief. This is a working hypothesis, not a commitment to build a complete editor.

## What we want to learn

Make expressive videos we enjoy, with intentional camera movement, recognizable forms, and room for surreal transformation. Build toward 30-second, one-minute, and eventually five-minute films assembled from manageable clips. The immediate priority is a usable creative workflow; improving image quality follows alongside it.

The core creative loop is: describe a shot, generate a short section, watch it, choose what works, and continue from a frame we like. Change the next scene, keyframe, camera path, model, or settings without losing earlier attempts. If a movie stops working halfway through, preserve the good part and branch from that point.

A working movie is a selection of ranges from saved generations. It is never the only surviving copy of those generations. Rejected attempts remain useful creative material and evidence about settings.

## Priorities

1. Organize projects and preserve every generation, its settings, and its parent frame.
2. Practice selecting, continuing, replacing, and assembling short clips.
3. Establish intentional depth-based 3D camera movement. 2D remains useful, but it is not the main destination.
4. Improve detail, temporal stability, and visual character through models, parameters, and ComfyUI workflows.
5. Grow duration once continuation and editing work reliably. Duration alone is not success.

Olof's first playback assessment: denoise 0.30 becomes too smooth; 0.50 flickers too much. Those are separate failure modes. The middle version is a useful comparison baseline, not an approved final recipe. Optical-flow alignment and learned frame interpolation are welcome experiments, including changes to the original stepped look when useful.

## Structure and style

Olof uses “structure” for recognizable subjects, object layout, silhouettes, building contours, and camera motion. “Style” includes patterns, textures, color, and artistic treatment. These are useful creative controls even though a generative model may entangle them. A moving camera can also be part of a style.

A later hypothesis is to author simple objects and camera paths in a small 3D scene, render guide footage, and translate its appearance while retaining useful structure. Test the translation on an existing short structured video first. Only invest in a 3D authoring system if that translation is convincing. Preserve this avenue as uncertain: drift, flicker, hidden surfaces, and imperfect conditioning could make it unsuitable. See [structure and style research](research/structure-and-style.md).

## Constraints

- Local Mac storage holds original references, all generations, and movie versions. Git holds small code/configuration/notes; it is not the video archive.
- Keep existing nodes where practical. Introduce a custom component only after a concrete missing capability is demonstrated.
- Use RunPod for heavy inference; use the Mac for planning, asset organization, preview, and editing.
- Initial budget: $50; Olof authorized spending the available balance for parallel experiments, including multiple GPU workers. Comparable output should stay near the SDXL cost; a pipeline approaching three times the measured recurring cost needs reconsideration rather than automatic adoption.
- Expensive image APIs may still make sense for occasional reference images or keyframes. Do not assume that makes them economical for every video frame.

## Build now and learn next

Completed: preserved project runs, continuation/cuts, depth guides, stronger camera comparisons and model stills. Next, practice visual storytelling, composition, lighting and editing alongside camera control; use the [filmmaking guide](research/filmmaking-for-ai-animation.md) to extract relevant craft. Stories can unfold through images, with music later and little need for dialogue. A timeline UI, automatic branching engine, reusable 3D engine and long unattended renders remain proposals.

Useful success evidence is practical: find a previous attempt; explain its settings; preserve a good opening while replacing its continuation; identify genuine parallax; and reproduce a working cut from its source ranges. Olof's playback review decides whether the movie is compelling.
