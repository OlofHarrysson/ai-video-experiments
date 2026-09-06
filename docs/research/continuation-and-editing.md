# Continuing, branching, and assembling a film

Researched 2026-09-06. Recommendation: practice one branch from a saved frame before making a longer movie. Begin with versioned cut notes and small clip renders; introduce a timeline engine after that practice identifies the missing behavior.

## Three different operations

- **Collect an existing job:** reconnect to ComfyUI and fetch the same result. Already implemented. It does not restart computation.
- **Creative continuation:** use a selected frame as the starting image for a new run, possibly with a new prompt or camera. This intentionally creates a new branch.
- **Equivalent resume:** interrupt a render, restore its full state, and continue as if it had never stopped. This is a stronger requirement and remains unverified.

A branching workflow does not have to promise bit-for-bit equivalence to be useful. It does need to preserve the accepted prefix, identify the exact parent frame, keep schedule timing understandable, and make any join inspectable.

## What the current node actually preserves

Difforum accepts `start_frame` and `end_frame`; schedules and incrementing seeds use the absolute loop frame. Its input image becomes the frame at `start_frame`, and the next sampled frame is `start_frame + 1`. `end_frame` is exclusive. It returns a batch only at the end of the node call, rather than saving a durable checkpoint after every iteration. [Pinned sampler source](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py)

The node also clones each call's initial image as its color reference. Continuing from frame 19 therefore changes that reference from the original frame 0 to frame 19. With color coherence enabled, a resumed chunk is not equivalent to the uninterrupted configuration. The static depth input and cadence/global frame phase also matter. This is why the current README's “resumable” capability needs an experiment before relying on it.

The local runner currently generates its initial image with `KSampler`, sets a frame count, and submits one batch. It does not upload a chosen parent frame, replace that initial-image subgraph, or pass a continuation range. New project folders do not add those capabilities by themselves.

## Minimal continuation experiment

1. Keep the existing source run untouched. Choose an exact generated PNG frame, not a screenshot or recompressed MP4 extraction when the original exists.
2. Prepare a branch graph using that image, global `start_frame`, full intended schedule horizon, and a short exclusive `end_frame`. Hold seed policy and camera settings fixed for the first comparison.
3. Record the parent run path, generated frame index, image SHA-256, global schedule frame, and intentional changes. Distinguish movie timeline time, source-frame time and schedule time.
4. Render eight new frames. Inspect the transition at normal speed, the last few parent frames, and the first few new ones. Keep every attempt.
5. Make a new cut referencing the old prefix plus the new continuation, without including the anchor twice. For example, retaining parent frames `[0,20)` includes frame 19; a branch batch starting at global 19 must contribute from its local frame 1 onward.
6. Replace only the continuation in another cut version. Demonstrate that the old cut and source assets still exist.

This experiment will determine whether existing nodes are sufficient or whether a small explicit color-anchor/checkpoint adapter is justified. Do not build that adapter before the missing state and expected behavior are agreed.

## State to preserve as the harness grows

A useful continuation receipt includes source pixels, parent identity, global frame, model/VAE/conditioning versions, exact graph, prompt/camera schedules, sampler settings, seed/RNG policy, color anchor, and aligned depth/control inputs. Some pipelines may also need latent or temporal state; that is model-specific. Preserve original references alongside the receipt. None of this implies that cross-version GPU rendering is deterministic.

A longer film can have deliberate shot boundaries and discontinuities. Plan a shot's purpose, start/end composition, camera move, approximate duration, and transition, then render manageable ranges. Grow from a short two-part scene to a 30-second assembly, then one minute, then five minutes. Repeatedly generating an entire long movie would make feedback slow and throw away useful work.

## Editorial representation

OpenTimelineIO records cut order, duration and references to external media. It does not contain the media or render the finished movie. That separation matches the intended workflow. It is a sensible later interchange format when an actual editor integration is needed; installing it now would not provide a review UI or a renderer. [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)

For now use the [manual cut convention](../workflow.md): versioned Markdown tables with explicit source FPS and half-open frame ranges. Keep cuts separate from generations and exports. This avoids committing to a custom timeline schema before practicing an edit.
