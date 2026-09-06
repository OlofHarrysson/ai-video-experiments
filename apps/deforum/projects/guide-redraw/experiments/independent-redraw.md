# Independent guide redraw

## Question and scope

Does restarting from each camera-only guide retain the boardwalk, observatory and foreground lantern better than sequential repaint feedback? Look separately at layout retention, texture flicker, edge artifacts and prompt/style quality. Eight consecutive frames at the original guide resolution, capped at 1280×720; no resizing, interpolation or crop during inference.

SDXL base 1.0, DPM++ 2M/Karras, 28 steps, CFG 6.5, denoise 0.40. Seeds are the guide's base seed plus its original frame index: 143–150 for positions 0–7 of the initial lantern recipe. Positive and negative CLIP conditioning and checkpoint come from the saved guide graph. The positive prompt is checked against this exact text:

> a moonlit marsh at blue hour, close tall reeds and a hanging copper lantern framing the left foreground, a winding wooden boardwalk over still water leading toward a distant small domed astronomical observatory, tiny amber lanterns along the boardwalk, luminous blue mushrooms, low violet mist, a crescent moon, cinematic wide composition, clear foreground middle ground and distant background, atmospheric dark fantasy illustration, textured painterly brushwork, deep teal and indigo with warm amber light

## Graph and transport

One lossless horizontal RGB PNG contains eight guides. At 1280×720 it is 10240×720. Existing `LoadImage` reads `anchor.png`; eight `ImageCrop` branches each select precisely one guide before `VAEEncode → KSampler → VAEDecode`. Seven `ImageBatch` nodes concatenate the decoded branches in source order. `SaveImage` node `11` is the sole output, matching the existing archive/collector contract. The full strip is never encoded or sampled as a latent.

Every original PNG is copied without rewriting its bytes, with a SHA-256 source map. Packing is checked by comparing every decoded crop byte-for-byte against its original RGB pixels. The graph and script are frozen alongside those inputs. No shared transport modification or custom worker node is needed.

## Execute

From `apps/deforum/`, using the app's locked environment plus temporary Pillow (no shared dependency edit):

```bash
uv run --with pillow python projects/guide-redraw/experiments/redraw.py prepare --guide-run projects/lantern-marsh/runs/GUIDE_RUN
uv run --env-file .env --with pillow python projects/guide-redraw/experiments/redraw.py submit --bundle projects/guide-redraw/references/assets/PRINTED_BUNDLE
```

`prepare` is local only. `submit` performs one paid shared-client submission and waits for the shared collector. It prints the job ID and receipt directory as soon as submission returns. Use the printed path exactly. A bundle permits only one submission attempt, including uncertain/failed attempts; inspect its run receipt before deciding on any new experiment. To reconnect, use the existing collector:

```bash
uv run --env-file .env python experiment.py collect projects/guide-redraw/runs/RUN_ID
```

Expected outputs: `frames/0000.png` through `0007.png` correspond to guide positions 0–7 in that order. `--start-frame N` selects N through N+7 and keeps seed indexing global. `submission.json` records `frame_map`, prompt graph hash and original guide lineage. The preview is one second at eight source FPS and 24 delivery FPS through repeated frames.

## Interpretation

Compare the same indexed positions from the parent feedback run. Feedback frame zero is the unchanged reference; redraw frame zero has undergone img2img, so exclude that pair from claims of equal denoising. Difforum also uses LAB color coherence 0.8, extra noise 0.02 and sharpening 0.2, absent here. Direct cumulative guide reprojection and successive feedback warps can differ. This is a practical workflow comparison, not an isolated causal test of temporal feedback.

An eight-frame successful output establishes the transport and independent branches, not long-shot stability. The prediction fails if retained guide geometry does not help or texture jumps make the clip less usable. Inspect actual frames and playback before drawing a preference.
