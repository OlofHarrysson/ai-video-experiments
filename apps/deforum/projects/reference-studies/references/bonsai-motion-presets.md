# SDXL Deforum motion-preset examples

Reviewed 2026-09-07. [Examples for SDXL Deforum Motion Presets](https://www.youtube.com/watch?v=vmKePs6iHs4), **The BonsAi Effect**, published 2024-07-15. Olof explicitly likes the video and supplied a link at **565s / 9:25**, inside **Evolve-Zoom-Slow-30s**, which starts at 9:18. The link does not establish a favorite among all the presets.

[Local study video](assets/artist-channel-2026-09-07/vmKePs6iHs4/reference.mp4) · [Source and hash](assets/artist-channel-2026-09-07/vmKePs6iHs4/source.json) · [Workflow and preset audit](../../../../../docs/research/bonsai-effect-workflow.md)

## Visual review

The compilation is a motion vocabulary demonstrated in one graphic world: cybernetic rabbits, human-like android faces, black-and-cream circuitry, cyan lights, hard outlines and rounded machinery. A simple repeated subject makes the differences easier to inspect, although subjects still transform considerably. It is a preset comparison, not a continuous narrative.

The chapter atlas contains **47 samples: the introduction plus 46 presets**, one representative image inside every chapter. All six pages were inspected. A still from each chapter reveals its visual character, not its motion speed; only the Evolve Zoom Slow interval received a dense temporal study.

| Chapter | What the sampled image shows | Useful distinction |
| --- | --- | --- |
| Classic 3D variants, 0:22–2:20 | Figures, machines and architecture become strongly tilted, stretched or pulled around a vanishing point. | Substantial view change can also deform geometry; a preset name is not proof of rigid 3D motion. |
| Classic Zoom Out, 3:49 | Tiny figures amid large architectural forms. | Scale and surrounding space can make a zoom meaningful. |
| Evolve Slow / Slow 2, 8:19 / 8:49 | Centered android figures against an organized circuit pattern. | A stable compositional center can coexist with changing objects and texture. |
| Evolve Zoom Slow, 9:18 | Rabbit becomes android; large face remains centered while the circuitry changes. | Best current target for a controlled morphing reproduction. |
| Fly Through / Spin, 10:18–11:47 | Faces and mechanical forms fill or cross the frame; the spin example has pronounced diagonal distortion. | Travel, subject replacement and image deformation overlap in the perceived effect. |
| Look Around / Move Around, 12:16 / 12:46 | More room-like arrangements, platforms, instruments and figures at different scales. | Promising composition references for a later intentional camera study. |
| Shapes variants, 19:12–21:40 | Circles, hexagons, kaleidoscopic geometry, frames and stars organize the artwork. | Motion guides can contribute a strong formal vocabulary without a complex simulated scene. |

### The supplied 9:25 interval

Fourteen samples at two-second intervals from **559–585s** show a rabbit changing into a human-like android by 561s, then a gradually enlarging face. The central eyes and mouth remain recognizable while ears, headgear, hair, cheeks and background circuits transform. By the later samples, the face is larger but still centered; the background's lines and circular lights have substantially rearranged. This feels visually different in its sampled progression from our large independent semantic redraws.

All **13 delivered frames at 565–565.4s** were also inspected. Differences over this short window are small: central facial placement persists while background circuitry shifts and some head details change. There are near-holds in the sequence; the source provides no manifest identifying original versus interpolated frames. This window is evidence of locally restrained change, not proof that the entire video has uniform smoothness.

[Detailed review, 26 unique selections across four pages](assets/artist-channel-2026-09-07/vmKePs6iHs4/evolve-zoom-study/v001/review.json)

![Continued face and circuitry transformation, 9:27–9:41](assets/artist-channel-2026-09-07/vmKePs6iHs4/evolve-zoom-study/v001/contact-sheet-003.jpg)

[Chapter atlas and timestamps](assets/artist-channel-2026-09-07/vmKePs6iHs4/chapter-atlas/v001/review.json)

## Creator-reported setup

The description identifies **Forge UI with Deforum, SDXL, `CHEYENNE_v16VAEBaked.safetensors`, seed 2215137870, and Illusionix LoRA at weight 1** with a short cybernetic-rabbit prompt. It reports FreeU and Kohya HR fix enabled at their defaults, landscape examples including presets originally intended for square output, and no post-processing of the examples. These are reported settings, not recovered execution logs. The stated defaults are not numerically specified.

In a [creator reply](https://www.youtube.com/watch?v=vmKePs6iHs4&lc=UgysgoAkRPFATNfBRcB4AaABAg.A5vDsbJ1ar9A5vhCyZo5_S), the artist attributes similar starting frames to the fixed seed and notes that presets with centered-symmetry prompt additions start differently. Their unsuccessful init-image attempt is personal experience, not a general technical prohibition.

The linked [Safety Marc presets](https://github.com/S4f3tyMarc/Deforum-Studio-Presets) and their hybrid-video archive were downloaded as research data. They target WebUI Deforum, **not ComfyUI**, and the files name Protovision XL rather than the artist's Cheyenne override. Their built-in RIFE/FILM options also mean that “no post-processing” cannot establish an absence of frame interpolation. Our downloaded compilation is 30 FPS; the inspected preset files use a 12 FPS timeline and ×2 finishing. The precise compilation/export path is unknown.

## The guide is surprisingly simple

The exact linked `Circle-Zoom-30s.mp4` is a white ring expanding on a black background. `Evolve-Zoom-Slow-30s.txt` combines optical flow from that guide with depth camera warping, while hybrid image compositing is disabled. It therefore uses the guide's movement without directly blending its black-and-white pixels into the artwork. This is separate from a ControlNet shape constraint and separate from RIFE finishing.

![Downloaded circle motion guide](assets/artist-channel-2026-09-07/hybrid-guides/reviews/Circle-Zoom-30s/v001/contact-sheet.jpg)

The neighboring Evolve Slow presets use an animated, approximately symmetric grayscale noise guide instead. Both guides are preserved under [hybrid-guides](assets/artist-channel-2026-09-07/hybrid-guides/), and the original ZIP plus hashes are retained. The [technical research](../../../../../docs/research/bonsai-effect-workflow.md) records the settings and their compatibility limits.

## Review boundary and next use

Archived 1920×1080, 30 FPS delivery, 1394.567256s. Automatic captions contain a brief spoken introduction and mostly music markers afterward; that introduction directs viewers to the description rather than explaining settings. Review comprises the six atlas pages and four targeted pages, plus six frames from each of two input guides. No full real-time audiovisual viewing, complete motion ranking of 46 presets, or generation run was performed.

This is a stronger engineering reference than an attractive film with no settings: we have a named preset, its source file, its input-motion video and the artist's model overrides. Reproduce a short segment of its mechanism before varying the camera. Preserve P3 + RIFE as our creative comparison, and keep depth-camera movement distinct from guide-induced morphing.
