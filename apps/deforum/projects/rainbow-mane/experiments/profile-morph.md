# Profile-to-horse drawing

2026-10-01. Steps 1 and 2 complete. Olof approves the drawing: “Yeah that is good! Lets continue with the next step.” The [guided Krea test](guided-repaint.md) follows this approved motion. This drawing itself uses no diffusion, generated head turn, camera movement or RIFE.

## Question and authorized scope

Olof finds the first generated passage's transformations too abrupt but says “the style is pretty good.” The next proposed experiment isolates a four-second profile-to-horse morph, with a drawn motion plan before Krea repainting. Olof requests “step 1,2 first.” This authorizes the profile drawing and its animation; step 3, using it to guide recurrent repainting, is deferred until this motion has been reviewed.

The original comic-print visual direction remains the target. The flat colors here make the geometry readable; they are not a replacement film style or a new generated opening. The drawing does not establish a successful turn from the previous three-quarter portrait.

## Drawing and timing

[Selected preview](../exports/profile-morph-v002/preview.mp4) · [six keyframes](../exports/profile-morph-v002/keyframes.jpg) · [source](profile_morph.py).

- One right-facing white character, one visible eye, rainbow crest and a fixed camera.
- 0.00–0.45 seconds: opening profile hold. The muzzle and jaw develop over 0.45–3.25 seconds. The ear rises over 0.65–2.90 seconds, and the crest extends down the neck over 0.50–3.35 seconds. Each progression eases into and out of its motion.
- 3.35–4.00 seconds: hold the horse endpoint. No body reveal is attempted.
- The same outline control points, eye, nostril and six ordered mane regions persist across all frames. Correspondences are saved in `landmarks.json`; editable SVGs and rendered PNGs are retained for every frame.

The project-specific Python script samples its cubic curves for supersampled Pillow rendering and exports the same curve definitions as SVG. FFmpeg encodes the 96 authored frames directly at 24 fps, 1280×720. It uses the existing locked Deforum environment and no new dependencies or cloud resources.

## Screening and revisions

`profile-morph-v001` reaches a recognizable horse in the assistant's six-frame overview, but the near ear pinches into a narrow line around 1.5 seconds. Its human and horse curves traverse their shapes in opposite directions. The source snapshot and original media remain preserved.

`profile-morph-v002` uses matching contour direction for the ear. The six-frame overview and every decoded frame from 1.25 through 1.667 seconds show the ear keeping visible area while it rises. The muzzle grows and the rainbow crest extends continuously in these inspected frames; the eye remains recognizable. The mane is deliberately a broad colored shape, and the endpoint is a stylized horse bust. Detailed hair, print texture and a full body are outside this guide.

Screened: six selected poses across each attempt, then all eleven decoded frames in the repaired window for v002. This supports the observed shape progression and ear repair. Olof subsequently approves the drawing and asks to continue with the painted test. The selected MP4 fully decodes to 96 frames at 24 fps, exactly four seconds. All 196 assets listed in its manifest match their SHA-256 hashes. Scoped Ruff checks pass.

## Next boundary

Olof has approved this drawing's motion and authorized the [guided repaint experiment](guided-repaint.md). The source drawing and point correspondences provide a motion plan; the drawing alone is not evidence of successful diffusion control. The painted experiment retains previous painting → spatial deformation → partial-noise repaint, with text conditioning throughout; guide blending is specified separately in its report.

Reproduce in a new, unused output directory from `apps/deforum/`:

```sh
uv run --locked python projects/rainbow-mane/experiments/profile_morph.py \
  --output projects/rainbow-mane/exports/profile-morph-v003
```

Each output includes its own source snapshot and hash inventory. Both attempts remain local in ignored exports; tracked source and this report preserve the recipe.
