# Guide → pixel movement → warp → repaint

2026-09-07. Completed: local optical-flow warps and six real ComfyUI repaint samples, with an interactive four-stage walkthrough. Stay with ComfyUI; A1111/Forge is deferred.

Use the artist's archived Circle-Zoom guide and two existing artworks: the Seedream marsh and a P3 portal frame. Compute DIS Medium optical flow at 1024×576 between source frames 72/73 (6.000/6.083 seconds), and separately 72/84 (6.000/7.000 seconds). The larger gap is a teaching example that makes movement visible, not the preset's normal per-frame timing. Both use warp factor 0.8. Arrow lengths can be magnified for readability without changing the applied displacement; label that separately.

Apply each measured field directly to artwork pixels using reverse remapping and reflected borders. Preserve full float fields, guide frames, originals and warped PNGs. The circle is never composited into the artwork. Estimate flow independently for each pair; the original animation's previous-flow warm start is not reproduced.

Repaint the original, the adjacent-frame warp, and the larger-gap warp with identical seed/prompt/sampler settings within each artwork. Use the installed SDXL base model; the portal retains its existing art LoRA. Use native ComfyUI img2img nodes, denoise 0.58, CFG 4.5, 18 steps, DPM++ 2M/Karras. This isolates the input-image difference while allowing diffusion to alter content. These are alternative next frames, not a temporally generated video sequence.

Review actual images before describing results. Show guide pair and arrows, a before/warp comparison, and warp/repaint comparison. Preserve a matched no-warp repaint so changes caused by ordinary diffusion are visible. The interactive walkthrough should expose both artworks and both time gaps without asking Olof to compare a large gallery from memory.

Source: [Deforum hybrid video implementation](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/hybrid_video.py), [archived preset study](../../../../../docs/research/bonsai-effect-workflow.md).

## Results

| Guide pair | Applied displacement, median | 95th percentile | Maximum |
| --- | --- | --- | --- |
| 6.000 → 6.083 s, adjacent frames | 1.24 px | 1.71 px | 2.43 px |
| 6.000 → 7.000 s, teaching example | 10.61 px | 16.99 px | 17.91 px |

These are measured at 1024×576 after multiplying the estimated flow by 0.8. The second row spans twelve source-frame steps; it is not a recommended per-frame camera speed. Display arrows are lengthened ×20 for the adjacent pair and ×2 for the teaching pair. Neither display scale changes the actual warp.

- **Marsh:** the warp displaces the existing lantern, boardwalk and observatory without inventing new objects. The repaint substantially redesigns the lantern and path and replaces the distant observatory with trees. The no-warp repaint also changes that distant content: those semantic changes cannot all be attributed to the ring. At these settings, diffusion has considerable freedom.
- **Portal:** the larger-gap warp expands and deforms the existing engraved rings. The repaint simplifies/rebuilds the machinery and changes the central light. The source already contains a circular portal; this is not evidence that white-ring pixels were copied into it.
- The two adjacent-input repaints remain broadly similar to their no-warp controls, with visible detail changes. The larger-gap inputs produce greater differences in these examples. This is a six-still mechanism study, not a temporal-consistency or aesthetic-quality benchmark.

All six repaint images and both source/warp comparisons were visually inspected. The dynamic arrows extend into black guide regions in this estimate: black is not an instruction to preserve artwork pixels. A sparse guide still leaves motion estimation ambiguous; it does not prescribe exact object geometry.

## User review and proposed next test

Olof rejects the repaint as an animation step: it looks like a completely new picture, whereas he wants gradual morphing over multiple frames or within parts of the image. The mechanism explanation is sufficiently understandable to move on, although understanding remains partial.

The no-warp control already redesigns the scene. Investigate repaint preservation before attributing the failure to guide flow. The marsh crosses from a Seedream source into SDXL base with a new prompt; model/style mismatch is a plausible contributor, not an isolated finding. Denoise 0.58 was borrowed from a strength translation in another recipe, without reproducing that recipe's checkpoint, conditioning or full feedback pipeline. This is not evidence that the original preset fails.

Proposed, not executed: screen three gentler denoise values (0.15, 0.25, 0.35) on the same marsh input with the actual adjacent-frame warp, holding the other settings fixed. Check source-to-repaint object and style preservation, then assess the best two in short feedback sequences for accumulated drift, blur, freezing and gradual change. These values are hypotheses specific to this setup; the liked P3 animation used a different recipe and higher denoise. Surface at most two meaningful video alternatives after assistant review. Preserve the planned move into intentional 3D camera work after this bounded calibration.

## Preserved outputs and reuse

- [Marsh overview](../exports/v001/marsh-walkthrough.jpg), [portal overview](../exports/v001/portal-walkthrough.jpg), [matched repaint gallery](../exports/v001/matched-repaints.jpg).
- [Source/flow manifest](../references/assets/v001/manifest.json): guide and artwork hashes, precise pairs, full-resolution flow files, applied displacement measurements and packed ComfyUI inputs.
- Runs `20260907T140019384304Z-marsh-matched-repaint-3f` and `20260907T140019438970Z-portal-matched-repaint-3f` preserve graphs, inputs, outputs and cloud receipts under `runs/`. Their transport-created `preview.mp4` files are sequences of comparison stills, not generated animations.
- `walkthrough.py prepare` builds the local example inputs. `repaint marsh` / `repaint portal` submits the installed native ComfyUI graph after configuring the existing endpoint through the serverless runbook. `present.py ABSOLUTE_FRAGMENT_PATH` creates the interactive walkthrough from these local files; its editable markup is `walkthrough-fragment.html`.

The deterministic warp currently runs locally; ComfyUI performs the real img2img stage. This demonstration adds no worker dependencies and does not yet integrate external flow into the full remote feedback loop. That integration and fresh-depth 3D movement remain the next implementation work.

## Validation and cloud cleanup

Three local tests passed: identity warp, known forward displacement direction, and matched sampler settings across the comparison inputs. The interactive stages, image/timing selectors, divider and no-warp control were checked at 736 px/light and 360 px/dark, with no page errors or horizontal overflow. Arrow visibility was inspected and corrected after the first browser check.

Reused the previously verified `f106834b7` worker image; no rebuild or model download package was required. Marsh queue/startup delay was 316.611 s and execution 23.631 s. Portal delay was 340.822 s and execution 11.229 s; the latter waited behind the first job on one worker. Capacity throttling was observed before a worker became available. Do not treat all queue delay as billed GPU time.

Verified all 16 cloud objects, 11,537,042 bytes, against local copies before cleanup. Endpoint min/max workers are zero, no workers or Pods remain, and the temporary volume was detached and deleted. Account balance decreased from $47.4156291391 to $47.3965197502, approximately $0.0191; reported current spend rate is zero. This is the observed balance change, not a separately itemized invoice. Private deployment/cleanup receipts are under `work/motion-guide-session/`.
