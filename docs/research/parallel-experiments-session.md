# Parallel experiment session — 2026-09-06

Four creative studies now have generated media, frozen recipes and local archives. Three subagents worked on independent model, settings and workflow questions while the parent ran the overscan study and managed shared infrastructure. All use the same lantern-marsh positive prompt where applicable.

## Review the results

| Study | Actual output | What it taught us |
| --- | --- | --- |
| [Lantern marsh overscan](../../apps/deforum/projects/lantern-marsh/experiments/overscan.md) | New 1280×720 SDXL reference, 24-frame depth guide, 24-frame feedback clip; three-second full/cropped exports | Cropping lowers final raw uncovered area from 10.8% to 7.6%, but interior disocclusion remains. Feedback fills gaps while changing scene structure. |
| [SDXL settings](../../apps/deforum/projects/sdxl-settings/experiments/settings.md) | Three 1024×576 stills; same prompt/seed, independently changed steps or CFG | Lower CFG gives calmer color in this sample; 20 steps retains useful detail. Neither fixes missing prompt objects. |
| [Models](model-comparison-session.md) | Two FLUX requests and one Seedream 4.0 request, all preserved | Seedream better realizes the lantern, distant observatory, crescent, blue mushrooms and painterly texture. FLUX size controls returned a square twice, with identical decoded pixels. |
| [Independent guide redraw](guide-redraw-session.md) | Eight independently repainted guide frames plus a guide/redraw/feedback comparison | Tests how much cumulative drift comes from feeding generated frames back into the next render. Redraw retained the guide structure better through frame 7, with more frame variation and a strong first-frame style jump. This one-second study does not establish long-shot temporal quality. |

[Model contact sheet](../../apps/deforum/projects/model-comparison/runs/20260906T215546Z-contact-sheet-f04e03ad/contact-sheet.png) · [three-second painted crop](../../apps/deforum/projects/lantern-marsh/exports/overscan-20260906T215334143141Z-overscan-24f/feedback-crop.mp4) · [full view left / crop right](../../apps/deforum/projects/lantern-marsh/exports/overscan-20260906T215334143141Z-overscan-24f/feedback-full-left-crop-right.mp4) · [guide / redraw / feedback comparison](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/preview.mp4).

These are small, controlled learning samples. Model stills differ in native resolution, negative conditioning and APIs; they do not prove animation cost or compatibility. Feedback and independent redraw also differ in color coherence, sharpening/noise and warp reuse, so their comparison is a workflow test rather than an isolated causal ablation. Video taste and flicker preference need playback review.

## Execution and concurrency

The custom ComfyUI endpoint allowed **three maximum workers**, minimum zero, with five-second idle timeout and 600-second job timeout. Olof explicitly authorized using the remaining roughly $50 RunPod balance for parallel experiments. The agents could submit independently; no one-worker restriction remains in the operating convention.

Five custom-worker jobs completed without provider-reported failures or retries:

| Job | Queue seconds | Execution seconds |
| --- | ---: | ---: |
| SDXL marsh reference | 147.007 | 8.532 |
| SDXL settings batch | 103.914 | 6.859 |
| 24-frame depth guide | 1.193 | 8.833 |
| 24-frame feedback | 1.156 | 88.069 |
| Eight independent redraws | 79.303 | 31.824 |

Three public image API calls completed separately. Their reported costs total $0.051. All five custom-worker job receipts identify the same warm GPU worker: allowing three workers and overlapping submissions did **not** guarantee simultaneous custom-job execution in this round. In particular, redraw queued behind feedback. Parallel agent preparation and public image calls still progressed independently. Several workers initialized during startup, but no throughput claim is inferred from their existence. Queue time is not billed GPU time.

The first submission after activation returned HTTP 409 with no job ID; health showed no new queued/running job before the later accepted request. The cause is unconfirmed. The rejected attempt remains local, and the client now retains future HTTP error bodies and submission-error receipts without retrying automatically.

## Preservation, cost and cleanup

Starting observed balance: $49.6992503705. After delayed charges posted, observed balance: $49.5480029076, a **$0.1512474629 account delta**, about fifteen cents for this round. The final reported spend rate was $0/hour. An earlier post-cleanup observation was $49.5959311298; it had not yet reflected all charges. This is account-level evidence, not an itemized final invoice. Managed image receipts account for $0.051; worker startup, execution, idle and storage are not fully separated by the balance delta.

Every one of the temporary volume's **109 objects, 102,783,302 bytes**, was compared byte-for-byte with its local archive, including auxiliary depth/masks and input/diagnostic files. Missing local objects were recovered. A second key/size/ETag listing matched. The endpoint was paused with min/max workers zero, the volume detached by REST v2 and deleted, and inventories confirmed zero Pods, zero workers and zero volumes. The active deployment file was moved into closed session receipts. Private verification and account responses are in `apps/deforum/work/overscan-session/`.

All original generations and derived exports remain under their projects on the Mac. They are ignored by Git; only recipes, reports and small workflow settings are committed. No separate-disk backup is configured. The retained endpoint and image can be reused after attaching a fresh archive volume.

## Next useful practice

Use the Seedream still as a deliberately composed keyframe, then compare short SDXL feedback and independent guide redraw from that same input. This separates spending on occasional high-quality scene design from repeated frame rendering. First inspect the current redraw comparison and choose the preferred structure-versus-morphing balance. Keep clips short and preserve every attempt; a new model's still-image quality alone does not justify adopting it for every frame.

Validation: 11 shared offline tests and four guide-redraw checks passed; the settings graph check and hosted-model plan also ran locally. Export probes confirmed three-second 24-FPS overscan videos and the one-second workflow comparison. Visual claims above come from original images and contact sheets; no perceptual playback rating is inferred from encoding checks.
