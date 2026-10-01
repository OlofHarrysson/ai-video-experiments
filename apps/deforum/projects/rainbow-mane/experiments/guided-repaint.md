# Guided profile morph: recurrent Krea test

2026-10-01. Olof approves the authored motion sketch: “Yeah that is good! Lets continue with the next step.” This authorizes a short painted test using the approved geometry, while retaining the comic-print direction.

## Question

Can a four-second recurrent Krea sequence follow the approved profile-to-horse motion while retaining the white/rainbow identity and the liked comic-print visual vocabulary?

## Inputs and method

1. **Sampling initialization:** the preceding generated painting is smoothly deformed using corresponding outline, ear, mane, eye and nostril positions from the approved drawing. A faint, feathered blend of the current drawing reinforces foreground geometry. The combined image is VAE-encoded and partially noised for the next repaint.
2. **Text:** a consistent comic-print description and staged human-to-horse descriptions. Frame numbers refer directly to the approved four-second, 24 fps drawing.
3. **Additional reference-image conditioning:** none. The sketch blend is part of initialization; its feathered region is a compositing weight, not a diffusion edit mask.

The opening is painted by Krea from the first approved drawing. Screen three opening noise strengths before choosing a source. Then inspect a short midpoint before completing 32 paintings at eight paintings per second. No camera movement or head turn is attempted. The original film and drawing remain preserved; a guided result is not assumed successful merely because it finishes.

The authored inverse thin-plate deformation is an approximate smooth field, not object tracking. Nearby background pixels can move too. Numerical preflight checks field orientation; visual review must separately assess shape, style and accumulation artifacts.

## Resources

Use the existing cached Krea model and pinned ComfyUI image. RTX 4090 is unavailable in the retained volume's EU-RO-1 data center; use one A100 80 GB PCIe at the observed $1.59/hour. The available balance was $13.67 before launch. Standing authorization in `docs/runpod.md` applies. Download and hash-check every generated image, then remove only owned compute and verified owned ComfyUI scratch files; keep the shared model volume.

## Results and recommendation

Completed: three opening probes and two four-second recurrent clips, 65 unique Krea jobs. [Review beside the approved sketch](http://localhost:3028/rainbow-mane-guided). The assistant recommends [the gentler repaint](../exports/guided-morph-v001/guided-n040-a012/rife/preview.mp4) for judging motion, with [the stronger repaint](../exports/guided-morph-v001/guided-n055-a012/rife/preview.mp4) as the meaningful alternative. Human judgment of these painted results is pending.

Opening probes use the same guide, text and seed with initial noise 0.65, 0.80 and 0.90. The 0.65 result stays close to the flat sketch. The selected 0.80 opening has a clear profile, hatched rainbow crest, violet dotted cheek shadow and cyan edge. At 0.90, a large duplicate face appears behind the character. All probes remain preserved. This opening is less visually rich than the original generated film frame; control has not yet recovered the full liked treatment.

Both sequences use the same selected opening, landmark motion, 12% foreground sketch blend, text stages and seeds. The only intended generation difference is initial repaint noise: 0.55 versus 0.40. Each produces 32 paintings on the approved 24 fps timeline, at frames 0, 3, 6, …, 93. RIFE 4.25 adds 62 intermediate frames and two final holds, giving 96 frames and exactly four seconds. Interpolation never feeds generation. Raw held-painting previews are retained for distinguishing generation defects from interpolation.

- **Stronger repaint, 0.55:** the main subject progressively develops a muzzle, rising ear and extended mane. Around 0.75–1.0 seconds, oversized faces emerge in the background and persist. The final horse has stronger shading and print detail, but the background competes with it. The muzzle remains more strongly redrawn than the drawing's precise contour.
- **Gentler repaint, 0.40:** the main silhouette follows the intended progression and the background stays comparatively quiet, without the dominant oversized faces. The ear, nose and mane retain doubled/translucent sketch contours, especially through the latter half. Some doubling is already visible in the original painted frames, so it cannot be attributed only to RIFE. The rainbow regions remain readable but lose saturation, and the treatment is softer and flatter than the original film's style.

This supports continued testing of explicit geometry for this morph. It does not establish exact pose control, a solved head turn, clean identity preservation or a finished visual style. A possible next experiment is to retain the landmark motion while reducing the black sketch outlines in the blended guide; that has not been run or selected.

## Screening and geometry checks

The first deformation fit folded a small area at guide frame 27. Increasing thin-plate regularization from 0.00001 to 0.001 produced nonfolding fields across all 31 planned steps: minimum sampled Jacobian 0.600. The fit is deliberately approximate: median landmark error 0.24 pixels, worst sampled error 19.92 pixels. It can transport nearby background detail and does not lock actual generated features to the guide.

Screened all three full-size opening images, early and midpoint source-painting sheets, both complete eight-frame overviews, and every decoded displayed frame in 1.625–1.875 and 2.875–3.125 seconds for both finished clips. The selected endpoint was also inspected at full resolution. These samples show the connected shape changes and the specific artifacts above; Olof's normal-speed motion and taste judgment remains pending.

## Verification and preservation

[Generation runner](guided_morph.py), [finisher](finish_guided.py) and [verification](verify_guided.py) use the existing app environment. The new shared landmark warp passes identity-pixel and inverse-translation tests. Scoped Ruff checks pass. All 65 jobs pass graph, input fingerprint, output hash and parent-lineage checks; all 192 finished frames pass hashes, and original paintings are preserved byte-for-byte at their delivery positions. Both MP4s decode to 96 frames at 1280×720 and 24 fps.

The public Pod proxy returned HTTP 403; the owned SSH tunnel reached the verified ComfyUI 0.34.0 runtime and all three pinned model hashes passed. ComfyUI adds an `is_changed` input fingerprint to PNG metadata; verification checks that fingerprint against the input hash before comparing the remaining graph. Per-frame receipts are immutable, so resumed collection does not overwrite a growing receipt or resubmit accepted jobs.

All 130 owned remote input/output files were checked against local originals before duplicate cleanup. The queue was empty, Pod `gg1zzozyabslfh` was deleted and absence verified; its SSH tunnel closed. The shared model volume remains. Estimated compute: **$0.5101**, excluding storage and not a final invoice. The media reviewer remains available for Olof, with source videos and frame provenance verified; no new browser-layout inspection was needed because the player layout is unchanged.

Configuration, graphs, input/output hashes, source snapshots and parent lineage live under `exports/guided-morph-v001/`; the approved geometry is `exports/profile-morph-v002/`. Both clips, all opening probes, failed preflight evidence and the original film remain preserved locally.
