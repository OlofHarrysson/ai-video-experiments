# Repaint every half-second versus every second

## Plan recorded before rendering

Olof accepts the 24 fps migration as visually identical and approves the proposed repaint-interval experiment. Generate two six-second shots from the same preserved Krea painting and absolute motion time (three seconds into the established twist/expansion path). Six seconds provides five repaint events for the slower branch. Use 24 fps for working and delivery timelines, the same three native Turbo intervals, prompt, model, seed progression per repaint, Lanczos motion and RIFE 4.25 settings. Only the repaint interval changes: 0.5 seconds (cadence 12, eleven new paintings) versus 1 second (cadence 24, five new paintings).

Each call initializes diffusion with the time-warped previous generated painting. Both branches use the same first repaint seed and increment once per repaint; fewer calls necessarily change seed assignment at a given time and reduce cumulative diffusion updates. Preserve every generation and raw frame. RIFE runs locally between the generated anchors at their original timestamps, with source rates 2/1 fps and multipliers 12/24. Retain native 24 fps warp-only motion after the final anchor: the last 0.5 second in the fast branch and 1 second in the slow branch. Neither shot is slowed down or looped to extend its duration.

Use the retained RunPod model/runtime cache on one short-lived owned Pod. Verify/download all files before deleting that Pod; retain the authorized network volume. Deliver a synchronized side-by-side comparison plus both individual finished clips. Review overview frames, selected every-frame transition windows and full-size interpolated frames. Temporal correspondence can soften or double fine details; do not infer playback preference from stills alone.

## Results

Both six-second finished clips are complete. **The one-second interval is the assistant's calmer audition candidate for Olof's stated aim of less frequent change.** The half-second branch is the more active alternative: later frames show more rebuilding of the little towers, arches and central flame. Both retain the warm cream/teal/orange palette and recognizable spiral composition. **Human feedback:** Olof selects the right-hand, one-second version: “a bit better” and “a bit more morphing.” Retain it for the [interpolation-scale follow-up](rife-scale.md).

![Half-second and one-second repainting, both with RIFE](../exports/repaint-intervals-v001/comparison/preview.mp4)

| Version | Working/delivery FPS | Cadence | New diffusion paintings | RIFE images between paintings |
| --- | ---: | ---: | ---: | ---: |
| Left: repaint every 0.5s | 24 / 24 | 12 | 11 | 11 |
| Right: repaint every 1s | 24 / 24 | 24 | 5 | 23 |

Individual finished videos: [0.5 seconds](../exports/repaint-intervals-v001/cadence-12/interpolated/preview.mp4), [1 second](../exports/repaint-intervals-v001/cadence-24/interpolated/preview.mp4). Raw diagnostic versions: [0.5 seconds](../exports/repaint-intervals-v001/cadence-12/preview.mp4), [1 second](../exports/repaint-intervals-v001/cadence-24/preview.mp4).

The retained paintings are endpoints for RIFE rather than images held on screen until the next repaint. RIFE spreads each redraw across the gap, so the slower branch still changes between its one-second endpoints. The first-pair midpoint checks show translucent/doubled fine lines in both branches. The selected window around four seconds approaches and leaves each generated endpoint gradually; it does not establish perfect correspondence or a final smoothness ranking. A full-size comparison at 4.5 seconds shows the half-second branch's more developed orange shell/flame and architecture, while the one-second branch retains broader forms. At that particular instant the fast branch is an actual diffusion anchor and the slow one an interpolated midpoint, so their sharpness is not an equal-phase comparison.

Motion timing is unchanged between branches. Both sample absolute time 3–9 seconds of the established path. The original twist reaches its scheduled limit at absolute second 5 (two seconds into these clips), while regional expansion continues. Different generated endpoints can still lead RIFE to infer different intermediate motion. The last 0.5/1 seconds use original native-24fps warped frames, respectively, because there is no later generated endpoint.

## Verification and execution

- Both versions use the preserved opening and the same Krea three-interval graph. Verified all sixteen requested/executed graphs, seed progression, parent/input/output hashes, successful ComfyUI histories, every reconstructed repaint warp, all 288 raw-frame hashes, and selected native 24 fps intermediate warps. No replay substitution or independent redraw was used: all sixteen were fresh diffusion calls on the same RTX 5090.
- RIFE 4.25 uses exactly the same pinned code, model weights and non-timing settings as the accepted baseline: full-scale float32 MPS inference, unchanged scale list and model flags. Inspected both first-pair midpoint images before full interpolation. All source hashes/mtimes and output hashes passed. All 18 generated/initial anchor images remain pixel-identical at their original timestamps after finishing. Raw, interpolated and comparison videos contain 144 decoded frames at 24 fps for exactly six seconds.
- First-pass visual review: both full-size first-pair midpoint images; six evenly spaced overview samples; every delivered frame from 3.916667 through 4.083334 seconds; and both full-size 4.5-second images. Contact sheets and decoded-frame receipts are beside the comparison. Sampled temporal inspection is not a human playback verdict.
- Reused the existing ComfyUI 0.34.0 runtime and all three cached Krea assets. Model verification took about 26.3 seconds; no model downloads or package installations were needed. RTX 5090 price was $0.99/hour. Median graph execution was 3.020/3.041 seconds; the first graph took 6.983 seconds. The full remote batch took 316.49 seconds including native warp generation and encoding. Raw 24 fps diagnostic construction dominated the post-inference work. RIFE inference took 37.31/36.31 seconds locally, excluding setup and encoding; early verified anchor downloads allowed that work to overlap remote diagnostics.
- Downloaded and verified all 559 archived files, including 32 remote input/output images. Archive SHA256: `182de60a830f08520b8774bda9d5e49e85dcf8e9985d49908df7215c33512986`. Early anchor archives were hash-verified and later matched against the complete archive. Confirmed an empty queue, deleted the owned Pod and verified its absence; the current Pod list was empty. The authorized 50 GB model/runtime volume remains. All media and receipts are local.

[Generation runner](repaint_intervals.py) · [verification and assembly](repaint_intervals_review.py). Private session receipts: `apps/deforum/work/repaint-interval-session/`. The three-step model recipe and interpolation settings remain unchanged. Olof's subsequent playback choice establishes one-second repainting as the new pacing baseline.
