# Filmmaking for image-led AI animation

Living research guide, 2026-09-07. Focus: directing, cinematography, visual storytelling and editing for short surreal films. Dialogue, screenplay formatting, actor management and production logistics are lower priorities. Music may come later. Reading this document does not establish Olof's understanding; feedback belongs in the [learning journal](../olof-learning-journal.md).

## Start with the change the viewer experiences

A shot can introduce a place, draw attention to a detail, withhold something, reveal it, or transform its meaning. Choose that purpose before selecting a camera move. The ASC's account of cinematographers breaking down a story connects changes in its dramatic beats to changes in framing, movement, lenses and lighting. We can apply this to a few visual beats without writing dialogue. [ASC: Analyzing a Script](https://theasc.com/article/shot-craft-analyzing-a-script/).

For our films, a useful starting question is: **What does the viewer notice at the beginning, and what is different by the end?** A loop can also work through rhythm or atmosphere rather than plot. The following priorities are our project-specific synthesis, not universal rules for good film.

| Craft | First thing to practice here |
| --- | --- |
| Direction | Decide what to show, when to reveal it, and which take serves that intention. |
| Visual storytelling | Build a small progression: an ordinary state, an interruption, a changed state. Recurring objects can connect the images. |
| Composition and staging | Make the important object readable; place other objects to guide attention or deliberately conceal information. Plan both the starting and ending frame. |
| Cinematography | Coordinate framing, perspective, light, color and movement around the chosen emphasis. |
| Editing | Select source ranges and order shots so each adds something. Control how long the viewer has to notice a change. |

Virtual images still benefit from this coordination. Pixar's account of *Toy Story 4* describes virtual cinematography as part of a sequence involving camera layout, animation and lighting, with technical choices serving storytelling. This supports learning film craft alongside model controls; it does not validate our current depth workflow. [ASC: Toy Story 4](https://theasc.com/article/toy-story-4-creating-a-virtual-cooke-look/).

## Direct attention with the whole image

Our practical scene checklist: identify one main point of attention, establish foreground/middle/background when useful, keep important silhouettes readable, and choose which information should remain hidden. Contrast, placement, scale and color are alternatives to constantly moving the camera. A beautiful reference should also leave room for the intended action and ending composition.

For the marsh, the warm foreground lantern competes with bright blue mushrooms and the distant dome. We can deliberately hand attention from one to another—for example, let the lantern dim before revealing a distant light. That is a proposed action, not a capability already demonstrated by the current runner.

Dark scenes need selective readability. ASC's lighting examples use silhouette, separation, localized pools of light and negative space to control what is visible. Darkness need not mean making the entire image muddy. Apply this by keeping the crucial contour or change visible against its background. Emotional associations with a color or composition depend on context; avoid rules such as “blue always means sad.” [ASC: Creating Visual Cues to Foster Fright](https://theasc.com/articles/shot-craft-halloween-horrors-creating-visual-cues-to-foster-fright).

## Camera rotation, travel and parallax

A **pan** turns the camera left/right from a fixed position; a **tilt** turns it up/down. A **truck** moves it sideways. A **dolly in/out** moves toward/away from the subject. An **orbit/arc** travels around a subject while adjusting aim to keep the chosen framing. Turning in place and moving around an object are different operations. [Adobe: Pan shots](https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles/pan-shot.html), [ASC: camera operation on Star Trek](https://theasc.com/podcasts/star-trek-motion-picture-richard-kline-david-mullen).

Nearby objects make translational parallax stronger: with a sideways camera move, they shift more than distant objects. They are useful, not mandatory for every effective shot. In the ideal pinhole model, pure rotation about the projection center changes viewing direction without depth-dependent translational parallax. A real camera rotating around an offset mounting point can include some translation. These distinctions follow from the projection model; they are geometry, not judgments of shot quality. [OpenCV: camera projection](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html), [Kaess et al.: rotation and translation in optical flow](https://www.cs.cmu.edu/~kaess/pub/Kaess09icra.pdf).

Zoom changes field of view from the same viewpoint; moving the camera changes perspective. James Wong Howe's *Hud* discussion makes this distinction while emphasizing movement that serves the action. A zoom can be an intentional stylistic choice, but enlarging a flat image does not recreate walking past objects. [ASC: The Photography of Hud](https://theasc.com/article/flashback-hud-1963/).

## A small shot vocabulary

Definitions describe the operation; effects and marsh applications are suggestions to test. A move has no guaranteed emotional meaning in isolation.

| Shot/control | Operation | Possible purpose and marsh exercise |
| --- | --- | --- |
| Locked camera, changing scene | Hold the viewpoint; move or change something within the frame. | Let the lantern flicker, a reflection change, or mist uncover the dome. Learn whether the event reads without camera travel. |
| Pan or tilt reveal | Turn from one composition to another. | Follow a trail of lights to the dome; end on new information. Plan the landing frame rather than only a rotation value. |
| Push-in / pull-back | Translate toward / away from the subject. | Approach a strange detail, or pull back to disclose its larger setting. Keep the chosen subject readable as perspective changes. |
| Sideways track / truck | Translate laterally. | Let reeds pass a distant landmark to make depth apparent. Keep travel within the scene representation's limits. |
| Arc / orbit | Travel around a point while maintaining deliberate aim. | Reveal another side of an object. Requires information about newly visible surfaces; our single reference does not supply that. |
| Pedestal / crane reveal | Raise or lower the viewpoint; crane paths may also arc. | Rise above reeds to reveal the marsh. Distinguish moving upward from tilting upward. |
| Dolly zoom | Translate while changing focal length/FOV oppositely, keeping subject size approximately constant. | Make the space around the lantern appear to expand or compress. Defer until subject framing and coherent perspective are controllable. |
| Rack focus | Move the plane of focus between depths; camera travel is optional. | Transfer attention from lantern to dome. This is a lens/attention technique, not translational parallax, and is not implemented in our current graph. |

Terminology references: [Adobe's shot glossary](https://helpx.adobe.com/uk/pdf/adobe_story_reference.pdf) and [dolly zoom guide](https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles/dolly-zoom-shot.html). The old glossary is used for vocabulary, not current software instructions; an arc does not require zooming. A digital scale change on one still cannot by itself reproduce the changing perspective of a true dolly zoom.

## Build sequences, not just moving postcards

Use shot size to change the information available: a wide view can establish the place, a closer view can isolate the event, and a later wide view can show its consequence. This need not become a rigid wide–medium–close formula. Before rendering, sketch three frames and write one short sentence about the change between each.

Our first story exercise could be **Invitation → Signal → Reveal**: establish the lantern and path; a light travels toward the dome; the dome opens onto an unexpected landscape. The progression is an invented brief for this project. Its object motion and reveal require separate implementation tests, so it is a proposal rather than the next automatic large render.

Assemble rough stills before expensive animation. If the order is hard to read, adjust composition or sequence first. Keep the successful images and take ranges, and change only the weak part. This extends our existing non-destructive workflow.

## Editing, rhythm and music

Cuts can clarify where we are, connect two images, skip time or deliberately disrupt continuity. Preserve screen direction and useful spatial relationships when the viewer is supposed to follow a journey. A match cut can connect similar shapes or actions; eye trace considers where attention lands across the cut. These are tools, not obligations to hide every transition. [Adobe: continuity editing](https://www.adobe.com/creativecloud/video/hub/ideas/what-is-continuity-editing-in-film.html), [cuts in film](https://www.adobe.com/creativecloud/video/post-production/cuts-in-film.html).

For our next assemblies, try a readable hold, a change, and time to register its result. Vary duration according to what the image asks the viewer to notice. Cutting every clip to equal length or moving continuously is not a substitute for choosing a progression.

Maryann Brandon describes rhythm as something an edit needs before music can support it. Start by checking whether our visual progression reads without audio, then experiment with musical phrases, accents, anticipation and pauses. This is a useful diagnostic, not a claim that music-led abstract films must work equally well in silence. Do not assume every cut should fall on a beat. [Film Independent: editors on rhythm and music](https://www.filmindependent.org/blog/j-j-abrams-long-time-editors-reveal-how-to-help-develop-characters-in-the-editing-room/).

## Apply the lesson from our completed render

The [Seedream motion experiment](../../apps/deforum/projects/seedream-motion/experiments/motion.md) produced clearly larger displacement, but the close lantern broke up. Its guide had 24.8% raw uncovered area by the last frame. Independent redraw retained more of the reference while failing to reconstruct the lantern; feedback painted over gaps but substantially changed the scene and style.

Our inference: nearby objects strengthen parallax **and** increase the burden of revealing unseen content in this representation. We need both a shot intention and a representation capable of that shot. “Increase the camera value” is not enough. Full orbits, large reveals and complex object action should remain unproven until tested; a depth map is not a complete 3D set.

Our exports also contain only eight distinct generated frames per second; encoding repeated frames at 24 FPS does not create smoother sampled motion. Geometry reconstruction, repaint variation and temporal sampling are separate issues. Stronger movement increases the visible jump between samples.

Recommended practice order: plan a three-image reveal; test a readable scene change with restrained camera travel; then compare push-in, track and arc using a purpose-built simple scene. Keep visual-story exercises distinct from geometry calibration. A scene need not have maximum camera motion to feel alive.

## A lightweight learning loop

Watch one short sequence and note the first focus of attention, the change, the camera's role, and the reason for the cut. BFI's analysis sheet prompts examination of framing, camera, light, sound and editing together. Our application: borrow one decision, test it in a short clip, and show the result in chat with a brief explanation. [BFI: Reading a Short Film or Scene](https://ugc.futurelearn.com/uploads/files/d3/95/d395220f-bbb0-4e76-810f-e3caca25727b/Reading_a_short_film_or_scene.pdf).

For each new experiment, record: **intention → start/end composition → scene change → camera choice → what must stay recognizable → intended cut**. Update this guide from actual results and Olof's feedback. Commercial tutorials and practitioners offer useful approaches rather than universal psychological laws; our workflow recommendations remain hypotheses until tested.
