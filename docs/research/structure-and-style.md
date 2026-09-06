# Structure-guided appearance and future 3D scenes

Researched 2026-09-06; deferred hypothesis. Olof wants recognizable structure and controllable motion with expressive, changeable appearance. Start by testing that balance on short existing footage before building a scene-authoring system.

## Creative framing

“Structure” can mean objects, silhouettes, pose, relative layout, building contours, and camera movement. “Style” can mean palette, textures, patterns, brushwork or the treatment of light. These are useful dimensions to ask for, not completely independent switches inside a diffusion model. Stylization can change perceived geometry, and a camera movement can itself be a stylistic choice.

The historical style-transfer analogy is useful: retain identifiable content while changing its visual treatment. The intended experiment does not require reproducing an older neural style-transfer architecture. A modern conditional image/video pipeline can be evaluated against the same creative question.

## Candidate routes

1. **Per-frame image translation with structural guidance.** Use matching depth, edge or pose conditioning and a style reference/prompt. Existing Difforum code can pass ControlNet and external control-image batches into sampling. Inspect the actual guide type and model compatibility; an RGB image is not automatically a valid depth/edge control signal. Independent redraws may preserve layout while flickering in texture. [Difforum ControlNet path](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py)
2. **A temporally trained video-to-video model.** VACE combines reference images and control videos. ComfyUI's official Wan2.1 VACE examples include a depth control-video workflow, making it a concrete route to test. It changes the generation system and cost profile; do not assume it will fit the SDXL budget or provide exact camera compliance. [Official ComfyUI VACE examples](https://docs.comfy.org/tutorials/video/wan/vace), [VACE implementation](https://github.com/ali-vilab/VACE)
3. **Authored 3D guide footage.** After a successful footage test, build a minimal scene with simple geometry and a known camera path. Render beauty/depth/edge or other supported guide passes; translate appearance with the proven route. This adds deliberate object/camera control but still leaves consistency and invented-detail problems in the translator.

The pinned Difforum repository mentions a Wan 2.2 VACE bridge, whereas the official ComfyUI page inspected here documents Wan2.1 VACE. Treat those as distinct integrations. Select and pin a specific workflow/model pair when running the test; do not mix names or weights based on a broad “VACE” label.

## First deferred test

Use a three-to-five-second clip we own or have permission to use, with clear foreground/background structure and a simple camera move. Save its original frames. Generate depth/edge guidance and inspect it, then compare two appearance strengths with the same structure inputs.

Review: are objects still recognizable, do silhouettes and spatial relationships remain useful, does camera motion follow the source, and do textures remain coherent? Check occlusions and thin objects. Record where the model deliberately reinterprets the scene versus where control fails. Keep both results and their guides.

If the result cannot retain enough structure, stop before investing in a 3D engine. If it works, a simple authored scene is the next test. A production scene editor, reconstruction pipeline, complex object animation, and automatic style disentanglement remain deferred.
