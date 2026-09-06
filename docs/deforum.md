# Deforum: image diffusion as animation

Deforum turns an image diffusion model into an animation system. Its characteristic look comes from repeatedly transforming and redrawing an image, rather than generating an entire temporally coherent video in one pass.

Research snapshot last reviewed: 2026-09-06.

For the current project practice, start with the [filmmaking direction](vision.md) and [working convention](workflow.md). The current priority is iterative editing and intentional 3D camera movement. Flow alignment and learned interpolation are welcome experiments when they improve the result; the stepped look is a creative option, not a fixed requirement.

## What I like about Deforum

This is a personal creative preference rather than a claim that Deforum is technically superior to newer video models.

What attracts me is its surreal, unstable quality. Images do not merely move through a scene; they continuously transform into new images. Shapes melt into one another, textures are reinvented, and the meaning of the scene can change while the camera keeps travelling through it.

In particular, I like:

- The morphing between subjects, materials, and environments.
- The stop-motion feeling created by visible changes from one frame to the next.
- The sense that each frame is being repainted rather than extracted from a perfectly coherent simulated world.
- Strong, explicit camera movement—zooming, rotating, translating, and warping—combined with semantic transformation.
- The intensity and unpredictability of longer sequences, where the animation can become a visual journey rather than a single generated shot.
- Imperfections such as flicker, drift, and unstable geometry when they contribute to the rhythm instead of merely looking broken.

Newer video-generation models are usually better at temporal consistency, realistic motion, and maintaining recognizable subjects. Those are real strengths, but consistency is not always the artistic goal. Their default outputs can feel polished yet generic: smooth cinematic movement, familiar compositions, and a recognizable “AI video” finish. That is the quality I sometimes mean when I call them *AI slop*.

The goal of these experiments is therefore not maximum realism or perfect continuity. It is **controllable instability**: deliberate camera choreography combined with surreal frame-by-frame reinvention. Deforum is interesting because its technical limitations naturally produce that aesthetic.

## The core loop

Conceptually, Deforum does this for each frame:

1. Generate or load the current image.
2. Move that image with a deterministic 2D or depth-assisted 3D transform.
3. Add the scheduled noise, prompt, and other conditioning for the next frame.
4. Run image-to-image diffusion to redraw the transformed image.
5. Save the result and feed it into the next iteration.

In compact form:

```text
previous frame
  -> camera warp
  -> image-to-image diffusion
  -> next frame
  -> repeat
```

The apparent memory is therefore mostly in the pixels carried forward from the previous frame. Classic Deforum does not need a video model with an internal representation of time.

## Where the camera movement comes from

The camera controls are image transforms applied before diffusion repairs and reinterprets the frame.

### 2D mode

The previous frame can be translated, rotated, zoomed, and sheared. Zooming enlarges or shrinks a flat canvas; translation pans across it. Newly exposed or enlarged regions are then invented by diffusion.

### 3D mode

Deforum can estimate a depth map, turn pixels into an approximate point cloud, move a virtual camera, and reproject the result. The scheduled controls include translation and rotation around the three axes, with perspective settings such as field of view and near/far clipping.

This is not a true persistent 3D scene. Classic pipelines can update depth as images change, but implementations differ. The pinned Difforum feedback sampler currently reuses its supplied depth map through the loop. That distinction matters for longer camera moves; see the [current 3D source audit](research/3d-camera-and-motion.md).

## Diffusion strength and the stop-motion character

The transformed previous frame is passed to image-to-image diffusion. Classic Deforum exposes a `strength` value, while the underlying denoising strength is its inverse:

```text
denoising strength = 1 - Deforum strength
```

Our selected Difforum node instead uses its strength schedule directly as denoise. The 0.30/0.40/0.50 experiment values are direct denoise values. Do not invert them when following the app runbook.

- Higher Deforum strength preserves more of the previous frame.
- Lower Deforum strength allows more aggressive redrawing.
- More redrawing creates stronger prompt changes and visual invention, but also more flicker and identity drift.

The result can resemble stop motion: every frame inherits the last composition, but the image model repaints texture, shapes, and detail instead of moving a stable set of objects through time.

## Prompt schedules

Prompts can be attached to frame numbers and interpolated over time. A prompt change does not directly move an object or camera. It changes what the diffusion pass is encouraged to see in the already-warped image.

This separation is important:

- The motion schedule determines the geometric trajectory.
- The prompt schedule determines the semantic trajectory.
- Diffusion combines them, repairing the warped image while introducing new content.

## Cadence

Deforum can diffuse only selected keyframes and generate intermediate frames by warping and interpolation. Higher cadence is faster and often smoother, but reduces the number of fully redrawn frames. Diffusing every frame usually produces the strongest hand-redrawn or stop-motion feeling.

## Why long clips drift

Because each generated frame becomes input to the next, small errors accumulate. Geometry, faces, textures, and depth can gradually mutate. A longer animation is therefore less like sampling independent images and more like repeatedly photocopying, moving, and repainting the same page.

The failure mode is also the appeal: temporal instability becomes an aesthetic rather than only a defect.

## A modern direction

The most promising way to preserve this look is not necessarily a modern text-to-video model. It is a modular workflow with:

1. A current image model.
2. An explicit 2D or depth-aware 3D warp between frames.
3. Controlled image-to-image denoising.
4. Frame-addressable schedules for prompts, camera motion, and strength.
5. Checkpointed segments so a satisfactory move can be preserved without regenerating the whole film.

ComfyUI is a natural host for that experiment because the transform, diffusion, depth, interpolation, and export stages can be separated and inspected. The main ecosystem options worth testing are:

- [Deforum ComfyUI nodes](https://github.com/deforum/deforum-comfy-nodes), the official but still work-in-progress direction.
- [XmYx Deforum Comfy nodes](https://github.com/XmYx/deforum-comfy-nodes), a broader community implementation built around established Deforum workflows.
- [Difforum](https://github.com/chillithebillis/Difforum), a newer attempt to combine Deforum-style animation with current ComfyUI image models.
- [KreaDeforum](https://github.com/Dream-Making-Git/KreaDeforum), an early integration experiment for Krea image models.

These projects vary in maturity. The architecture is more important than any single extension: explicit warping plus image-to-image feedback is the part that creates the Deforum character.

## Primary references

- [Deforum renderer feedback loop](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py#L412-L469)
- [2D and 3D frame transforms](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/animation.py#L173-L230)
- [Image-to-image denoising-strength conversion](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/webui_sd_pipeline.py#L21-L50)
- [Cadence and tween generation](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py#L295-L399)
- [Deforum animation settings](https://github.com/deforum-art/deforum-for-automatic1111-webui/wiki/Animation-Settings)
- [Deforum animation examples](https://github.com/deforum/sd-webui-deforum/wiki/Animation-Video-Examples-Gallery)
