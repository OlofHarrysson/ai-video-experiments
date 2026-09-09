# AI-controlled animation software

Research date: 2026-09-09. Scope: conventional animation authoring through scripting or APIs, excluding image-to-video generation. Documentation and selected source inspection only; no authoring integration or animation quality test has been run.

## Recommendation

Test Blender first as an animation authoring engine controlled through its Python API. This recommendation is based on its documented control surface, editable scene format, and available animation tools, not a demonstrated result with our puppy characters. Moho is the strongest alternative to investigate if a drawn 2D puppet workflow is the priority.

Our earlier puppy edits did not produce satisfying character performance. A conventional rig gives the experiment a different foundation: persistent body geometry or drawings, explicit controls, and editable movement curves. Artistic quality still depends on the asset, rig, poses, timing, and review.

## How animators build movement

Common approaches are hand-drawn 2D, rigged 2D, and rigged 3D. In hand-drawn work, artists create key poses, then breakdown drawings that define how the action travels between those poses, then additional drawings and cleanup. Breakdowns need not be geometric or temporal midpoints. Storyboards and an animatic establish the scene and timing before finished animation. See Toon Boom's [paperless workflow](https://learn.toonboom.com/modules/animation-workflow/topic/paperless-animation-workflow) and [key and breakdown definitions](https://docs.toonboom.com/help/harmony-21/advanced/paperless-animation/about-mark-drawing.html).

Rigged animation prepares a reusable character with controls. Artists block the significant poses and timing, refine movement curves, and polish overlapping actions. Moving a paw target can bend its connected leg through inverse kinematics; the artist still chooses the target path, contact timing, and body motion. Computer interpolation supplies values between keys, but does not independently determine good acting. Animation Mentor describes this progression in its [blocking, splining, and polish guidance](https://www.animationmentor.com/blog/tutorial-how-to-polish-your-animation/).

For a puppy hop, an example pose plan is crouch, push-off, apex, landing, and recovery. The important work includes weight transfer, convincing paw contacts, the body's travel arc, and ears and tail following the main action. Rendering more frames alone does not establish these decisions.

## Software and agent access

| Software | Documented capabilities | Assessment for this experiment |
| --- | --- | --- |
| Blender | Python scripting; skeletons, constraints, inverse kinematics, animation curves, shape keys, and rendering. Grease Pencil supports drawings and bone-weighted strokes. | Best first automation probe. Can author persistent scenes and render through scripts. A suitable character asset and rig remain substantial work. |
| Moho | 2D vector and bone animation, inverse kinematics, Smart Bones, and Lua scripting. | Promising for expressive drawn puppets. Lua support is verified; the exact external, unattended authoring route needs a local test. |
| Toon Boom Harmony | QtScript scene automation; extended drawing tools and Python interfaces. Documented Python batch sessions can run outside the GUI. | A credible professional 2D option with real automation, although selecting an edition and validating the installed API are prerequisites. |
| OpenToonz | Plastic mesh and skeleton deformation in the application; ToonzScript exposes images, levels, scene cells, transforms, and rendering. | Useful animation software, but the inspected script reference did not establish complete Plastic rig creation and bone-keyframing access. Do not assume its full UI is scriptable. |

Primary references:

- Blender: [general features and Python](https://www.blender.org/features/), [animation tools](https://www.blender.org/features/animation/), [Grease Pencil](https://www.blender.org/features/story-artist/), and [command-line arguments](https://docs.blender.org/manual/id/dev/advanced/command_line/arguments.html). The last page is an official development-manual reference; validate against the installed version before implementation.
- Moho: [current features and Lua scripting](https://moho.lostmarble.com/pages/features) and [publisher-hosted 13.5 manual](https://www.lostmarble.com/manual/13.5/Moho%20Users%20Manual.pdf). The older manual is supporting context, not a current API compatibility guarantee.
- Harmony: [version 25 scripting overview](https://docs.toonboom.com/help/harmony-25/advanced/scripting/about-scripting.html), [version 24 external Python sessions](https://docs.toonboom.com/help/harmony-24/scripting/python/index.html), and [version 24 JavaScript batch invocation](https://docs.toonboom.com/help/harmony-24/scripting/script/index.html).
- OpenToonz: [Plastic animation](https://opentoonz.readthedocs.io/en/latest/create_animations_using_plastic_tool.html) and [ToonzScript API](https://opentoonz.readthedocs.io/en/latest/toonzscript.html). The API limitation above is an inference from the documented surface, not proof that deeper integration is impossible.

## Existing bridge versus custom tooling

Blender can execute an authoring script directly:

```sh
blender --background scene.blend --python animate.py
```

The community [Blender MCP project](https://github.com/ahujasid/blender-mcp) already provides an agent connection. Its [server source](https://github.com/ahujasid/blender-mcp/blob/main/src/blender_mcp/server.py) exposes Python execution, scene inspection, and viewport screenshots. It is a third-party bridge, not Blender's official API and not an animation system by itself. It has not been installed or tested here.

Start with direct Python rather than adding a bridge immediately. Any custom code should be a small convenience layer for named rig controls, keyframe edits, saving versions, and producing review renders. Blender should continue to own deformation, curve evaluation, scene persistence, and rendering.

## Proposed first proof

Use one suitable rigged character on a plain floor. First verify that a script can change a pose, keyframe it, save the project, reopen it, and render the expected result. Then author a three-second play bow and small hop, with visible full-body movement. Review playback for weight, paw sliding, arcs, readable silhouette, and secondary motion before investing in the park, second dog, or final style.

Deliver the editable project alongside its preview so individual poses and timing can be inspected and revised. A successful API test would prove access; only the resulting movement would justify expanding this into a film.
