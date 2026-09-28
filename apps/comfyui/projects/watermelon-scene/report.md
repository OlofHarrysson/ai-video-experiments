# Watermelon in a scene: results

2026-09-28. **A rendered circle over a background photo gives useful control of watermelon placement, lighting and contact shadows. The strongest tested route is Sunburst with a fixed fruit reference, followed by deterministic background compositing. Native video generation follows the broad motion but does not yet preserve the requested orientation.** These are assistant-screened results from one scene, pending Olof's taste review.

## Watch the comparison

- [Four-panel, five-second comparison](exports/video/comparison.mp4): authored guide; seven independently generated Sunburst images; LTX 2.3 with three scene keyframes; H3 Max with a first-scene reference. Watch the rind rotate in the native videos and the background texture change between independent images.
- [Sunburst with the original background retained](exports/video/background-locked-stills.mp4): the same seven images, held without interpolation, composited through a feathered fruit-and-shadow region. This is a placement/continuity diagnostic, not smooth finished animation.
- [Still comparisons](exports/stills/comparison-0.jpg), [remaining stills and mask failures](exports/stills/comparison-1.jpg), [aligned fruit crops](exports/stills/sunburst-aligned-rind.jpg).

## What worked and what failed

| Experiment | Observed outcome | Practical meaning |
|---|---|---|
| Sunburst: photo + circle + fixed fruit reference, seven positions | Believable insertion and soft shadows; centre errors approximately 5–8 px at 1024 square; equivalent diameter within -2.7% to +3.3% | Best tested still recipe. Broad rind pattern survives, but fine details and background texture still change |
| Seedream 5 Pro: same inputs, left/middle/right | Centre errors approximately 3–8 px; diameter within -3.9% to -1.4%; plausible but stronger and longer shadows | Good placement alternative. More visible changes to the tabletop and its illumination |
| Full scene from a flat layout + fruit reference | Both made coherent photographic scenes. Seedream: about 6 px centre error and +1.4% diameter. Sunburst: 22 px and +7.9% | Generating the setting and positioned fruit together works too; it does not retain a preselected room |
| Sunburst with transparent edit mask | Rebuilt the room and misplaced the fruit by about 284 px | Failed this submitted recipe. Mask interpretation/integration is not established; this is not a universal claim about the model |
| Sunburst with black/white edit mask | Centre accurate, fruit about 11% larger than the 260 px circle; background changes remained | No preservation advantage here. The edit region deliberately included extra space for a shadow, so its extent was larger than the object guide |
| LTX 2.3 Quality: moving guide + first/middle/last scene images | Approximate mean path error 14 px, maximum 28 px. Rind turns significantly around 2–3 seconds, then changes back toward the endpoint appearance | Promising path control; failed the requested rigid, non-rotating translation |
| H3 Max: moving guide + first scene image | Approximate mean path error 53 px; ends around 70 px from target. Fruit rotates; framing and size drift | Plausible motion, weaker adherence to this precise guide |
| Wan 2.2 VACE: background video + moving edit mask + fruit reference + first-frame anchor | Fruit appears in the first frame, then disappears; orange outline-like artifacts follow the mask region | Failed this integration/recipe. No claim that VACE inpainting universally fails |
| LTX follow-up: same seed and anchors, guide strength 0 instead of 0.8 | Approximate mean path error 33 px, maximum 66 px; conspicuous green ring in the first half | Strong guide conditioning helped this example. One comparison is not a general benchmark; zero strength is a parameter ablation, not proof that all video input information is removed |
| Remotion compositing of the seven Sunburst outputs | Checked centre-frame PNG retained all 904,666 pixels outside an expanded edit region exactly | Background preservation can be enforced in the compositor, independently of model obedience. Local edge/shadow blending still needs visual review |

All paid jobs have returned a saved result: 15 still images, four generated videos and one validation rejection. No paid request remains pending.

## Inputs and meaning of the controls

The background is a newly generated 1024-square kitchen photograph with distinctive wood grain, a window on the left, utensils and a shelf. Remotion overlays a green SVG circle. The model receives a raster PNG of that composition plus the same selected watermelon reference on each independent request. **That coloured guide is an ordinary input image, not a depth map or a formal inpainting mask.** No adapter is needed for this image-editor route.

The target circle has radius 130 at y=650 and moves from x=250 to x=770. The authored sequence contains 81 frames at 16 fps; seven image samples are taken at source frames 0, 13, 27, 40, 53, 67 and 80. Their x positions are 250, 334.5, 425.5, 510, 594.5, 685.5 and 770. The centre keyframe is x=510, not 512.

All insertions ask for one fruit, constant size/orientation, relighting from the left window, contact shadow and unchanged surroundings. Full-scene tests instead receive a simple wall/table/window layout. The alpha and black/white mask experiments also receive the coloured scene guide and fruit reference; they differ by the additional mask encoding. The editable area includes a radius-145 circle plus an ellipse under the fruit to allow a shadow.

LTX receives the rendered guide video and three accepted Sunburst scene images. Its built-in control preprocessor remains enabled; we did not supply a hand-built depth map. Requested resolution was 768 square, but the actual built-in-control output was 704 square, 81 frames at 16 fps. H3 receives the RGB guide as reference footage, not a hard mask or ControlNet signal; the accepted version used 24 fps guide footage and returned 768-square, 124-frame video at 24 fps. Its requested duration was 5 seconds; the actual video lasts 5.167 seconds. The original 16 fps guide was rejected during validation, preserved as a failed request, then resampled for one successful retry.

These video comparisons are recipe comparisons, not matched-input model rankings: LTX has three scene anchors; H3 has one. All requested seeds are 43 where supported; Sunburst and Seedream endpoints did not expose seed controls in the inspected schemas.

VACE receives the static background video, a moving black/white edit-mask video, the fruit reference and the accepted left-position first-frame image. It used 40 steps, CFG 5 and no interpolation, with input preprocessing disabled. The requested 720p tier returned a 960-square, 81-frame clip at 16 fps. Although a frames ZIP was requested, the response returned `frames_zip: null`; the original video is preserved. The fruit disappears immediately after the supplied opening frame. [Failed clip](runs/video/vace-mask-anchor/output.mp4) and [every-frame opening inspection](exports/dense-vace/v001/contact-sheet.jpg).

The compositing variant uses the untouched background as a base and reveals each generated image through a soft circle and shadow ellipse. It adds no new generated frame. It locks distant pixels while allowing generated lighting/shadow near the fruit; it does not solve rind consistency, arbitrary occlusion or moving-camera scenes.

## Recommendation

Use **Remotion guides → Sunburst scene keyframes → controlled compositing** for the next small animation study. Keep the background as a separate layer and use the same fruit reference throughout. This gives useful position/size control and a concrete way to retain the setting. Seedream is a credible lower-cost still alternative, with a different shadow treatment in this scene.

Keep LTX as an optional motion experiment. A circle communicates position and silhouette but says very little about the fruit's rotation or surface orientation. Before attempting a bat strike, test a richer guide or a rigid animated fruit asset that explicitly carries orientation, then evaluate whether video refinement respects it. The current clip does not establish impact, fracture, occlusion or physically correct destruction.

The reusable part for Deforum is the authored geometry and layer/mask sequence. This experiment does not change Deforum's Krea recipe or install a new runtime. The shape-to-image route can operate separately while its controls are tested.

## Evidence and limitations

All 15 generated stills were screened in contact sheets, with selected full-size images and contour overlays. Seven aligned Sunburst fruit crops expose changes in detail and orientation. Native videos were reviewed with nine evenly spaced frames each; LTX and H3 also received every-frame checks in representative good and rotating intervals, and VACE's first quarter-second was checked frame by frame. The Remotion comparison's middle frame and encoded dimensions/timing were checked. This is frame-based assistant screening, not a claim of human real-time playback approval.

Geometry uses approximate colour-based foreground segmentation, largest-component selection and hole filling. Cyan contours and pink targets are retained for inspection. Dark rind boundaries and highlights can bias estimates; values are useful diagnostics, not ground truth. The final video estimator excludes saturated synthetic green so the failed LTX run's green ring is not mistaken for the fruit. Its first unfiltered metric was discarded after visual inspection identified that failure. Video path diagnostics normalize the intended path over each returned clip's frame count.

Missing fruit is explicitly reported as a failed detection, never zero positional error. VACE has a detected fruit in only one of 81 frames, so its whole-clip position statistics are null.

Background RGB differences outside a generous object/shadow region average roughly 3.4–4.5/255 for Sunburst and 6.3–7.3/255 for Seedream. This includes illumination, shadow spill and texture changes, not just camera displacement; it is not a general preservation score. Exact background retention was separately verified on the compositor's PNG. H.264 compression can change pixels even in nominally static regions.

[Run index](run-index.json), [still measurements](still-measurements.json), [video measurements](video-measurements.json), and [compositor verification](background-lock-verification.json) preserve the compact evidence. Raw input/submission/result receipts, originals, hashes and media remain in ignored local `runs/`, `references/assets/` and `exports/` folders. Media is locally preserved, not included in Git or independently backed up.

## Pricing sources and accounting

The user authorized $10 and one hour beginning 11:23:36 UTC, deadline 12:23:36 UTC. Only Fal was used; no RunPod infrastructure or development server was created. New spending excludes the earlier fruit reference and earlier experiments.

- [Sunburst](https://fal.ai/models/openai/gpt-image-2.5/sunburst/edit) is token billed; the published high-quality 1K one-input illustration is about $0.05268, not an invoice for our two-input edits. We used $0.10/image for a working estimate and reserved $0.25/image.
- [Seedream 5 Pro](https://fal.ai/models/bytedance/seedream/v5/pro/edit) costs $0.0675 for this output size plus $0.0045 for the second input: $0.072 per edit.
- [LTX 2.3 Quality](https://fal.ai/models/fal-ai/ltx-2.3-quality/reference-video-to-video) is $0.0024075 per rounded-up output megapixel. Each actual 704×704×81 clip is about $0.099 on that basis; $0.20 was reserved per request.
- [H3 Max](https://fal.ai/models/minimax/h3-max/reference-to-video) charges $0.08/output-second at 768P plus reference tokens above its allowance. We reserved $1.25 for the successful request and retained another $1.25 contingency for the rejected submission; exact billed usage is not exposed by this connector.
- [VACE](https://fal.ai/models/fal-ai/wan-22-vace-fun-a14b/inpainting) costs $0.10/second at 720p, with seconds based on 16 fps: approximately $0.506 for 81 frames.

Total reserved across the 20 submissions is **$6.448**, including the rejected H3 request at its full allowance. A working estimate using $0.10 per Sunburst image, the successful H3 allowance and published video/image unit prices is about **$3.35**. Neither amount is a verified invoice; the reserve deliberately accommodates uncertainty while staying below $10. There were 11 Sunburst and four Seedream image outputs.

The H3 frame-rate validation issue is recorded as AF-20260928-135035 in the central agent-friction log. A completed queue status can still yield an error on result retrieval; result payloads must be checked separately.
