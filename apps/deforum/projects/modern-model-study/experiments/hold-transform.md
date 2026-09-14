# Hold a moving scene, then deliberately transform it

Plan recorded before inference, 2026-09-14.

Olof reviewed the preservation diagnostics and found most static or too similar to be interesting films. He approves taking low noise into an actual moving shot with a deliberate transformation ramp. Preservation is useful only if we retain expressive motion and scene changes.

Two matched eight-second clips begin from the liked brass-snail painting and move into a canyon city. Both retain recurrent previous-image initialization, independent incrementing seeds, Krea Turbo, Euler, CFG 1, three proportionally scaled sampling intervals, two paintings/second, 24 fps working/delivery timelines, Lanczos spatial warping and RIFE 4.25 scale 1 finishing. No image reference adapter, latent-history blend or copied-back protection mask is used.

The opening subject moves while its text stays unchanged through 1.5s. At 2s it becomes a shell inhabited by buildings, at 3s a hollow architectural shell, and at 4s a canyon-city environment. A broad twist/expansion settles before a smaller counter-turn and sideways move settle at 7.5s. The final half-second holds the final painting.

- **Usual holding noise:** 0.60 before the transition and 0.64 afterward.
- **Low holding noise:** 0.10 before the transition and 0.10 afterward.
- **Identical transformation in both:** noise rises from 0.40 at 2s through 0.44, 0.53, 0.65 and 0.74 to 0.78 at 4.5s, then falls through 0.74 and 0.68 to 0.64 at 6s. From 6.5s each branch returns to its holding value. These values are starting noise levels, not CFG or the old denoise-fraction setting.

This isolates the holding policy around an identical transition ramp. The prior-image state at the start of that ramp will differ, which is an intended consequence of recurrent feedback. The comparison is a fresh matched pair, not a reproduction of an earlier complete film.

Inspect all sixteen paintings per branch, matched detail crops during the unchanged-text portions, and intermediate frames around the largest painting change. Check whether low noise preserves the snail and finished buildings without preventing conversion or losing too much shading. Do not infer aesthetic improvement from lower pixel differences. Present the pair in the linked reviewer and a concise chat preview.

Reuse the retained model volume with one owned short-lived Pod. Target less than $1 incremental cost; archive and verify all results before deleting the owned Pod. Keep the authorized model cache.

## Results

The assistant's candidate is **low-noise holding**. It retains more of the snail's fine radial engravings and gold crack-like highlights during the first three repaints, and the finished city undergoes fewer small architectural revisions in the final three. Both branches successfully convert the shell into an open arch overlooking a city at 4s. Low noise does not prevent this deliberate transformation, but neither branch removes the large redraw between 3.5 and 4s. Olof subsequently likes the low-hold version but identifies late settling; see the feedback below.

The opening is not a static hold: the same expansion and twist move both subjects. At usual noise the snail's marks and foot are reinterpreted more; low noise largely carries the original design along with that motion. In the ending, low noise retains the prominent right-hand tower, gold balconies and roof forms while the counter-turn settles. Surface shading remains readable over this short hold. This does not contradict the earlier flattening diagnosis over many repeated low-noise updates.

Mean absolute RGB difference between the warped input and resulting painting is 0.03160 versus 0.01223 during the opening, and 0.04845 versus 0.01018 during the ending (usual versus low). These measurements describe redraw magnitude, not crispness or perceived video quality. The branches reach different cities because each consumes its own previous painting; there is no later state reset.

The comparison supports trying **low holding noise as a scene-level control**, not changing every repaint to 0.1. Keep the transition ramp separately adjustable. The remaining challenge is to make the shell-opening event itself unfold more gradually while retaining its clear environmental change.

### Playback and evidence

- [Synchronized local reviewer](http://localhost:3028/): two videos, shared timeline and painting stepping, with plain-language generation details.
- [Chat comparison](../exports/hold-transform-v001/comparison.mp4): usual noise on the left, low holding noise on the right.
- [Usual holding](../exports/hold-transform-v001/usual-hold/section-016/rife/preview.mp4) and [low holding](../exports/hold-transform-v001/low-hold/section-016/rife/preview.mp4).
- [Source review sheets](../exports/hold-transform-v001/review/) and [generation verification](../exports/hold-transform-v001/generation-check.json).

The main review covers all 32 source paintings, early and late native detail crops, the first interpolation pair, five frames across the 3.5–4s shell-opening event, and eight consecutive crop frames at 4.208–4.5s (the largest mean RGB repaint change). At the shell opening, RIFE briefly combines solid-shell markings with the emerging city; subsequent bridge and balcony edges also double or soften before settling. This is selective frame-sequence review, not inspection of every video frame. The local browser shows both full frames together, advances both to frame 12 / painting 1, and plays them on the linked timeline.

[Delivery verification](../exports/hold-transform-v001/delivery-check.json) passes all 30 job histories, prompt IDs, parent/output hashes and pixel-exact recomputation of the warped initialization. ComfyUI adds a `LoadImage.is_changed` signature to the PNG's embedded graph; it matches the actual input SHA-256 in every job, and the remaining graph must match exactly. Both eight-second, 1536×1024 videos fully decode to 192 frames at 24 fps. Their PNG timelines preserve all sixteen anchors, contain 165 RIFE intermediate frames and eleven final hold frames. Browser playback reaches frame 191 in both clips; the reviewer is rewound and left running through Devrun for Olof.

All 30 new GPU jobs are archived locally; 632 archive files passed SHA-256 verification. The owned A100 Pod and 60 owned remote input/output files were removed; the retained model volume is preserved. Conservative estimated round cost is **$0.26**, including a disk allowance; this is not posted billing. No new models or custom nodes were installed.

## Human feedback and earlier settling — 2026-09-14

Olof says the right-hand low-hold version is pretty good, but reports continued flicker around delivery frames 105–132 and thinks the drop to low noise happens several paintings too late. He asks whether image changes can be measured and used to decide when to settle. This is a proposed adaptive control, not an approved implementation or evidence that a particular change threshold works.

Inspection of frames 96, 105, 108, 120, 132 and 156 supports the timing concern: the open city exists at painting 96 (4s), but starting noise rises further to 0.78 at painting 108 (4.5s), remains 0.744 at 120 and 0.676 at 132, and only reaches 0.1 at 156 (6.5s). There is no automatic completion detector: the current schedule is driven by time. [Matched frame sheet](../exports/hold-transform-v001/review/human-feedback-105-132.jpg).

The existing metric compares each newly painted image with its **warped initialization**, so intended spatial motion is already included in the reference. It is normalized mean absolute RGB difference, not percentage of changed pixels or a perceptual quality score. Low-hold redraw magnitude is 0.0787 at frame 96, 0.0888 at 108, 0.0686 at 120 and 0.0542 at 132, falling to 0.0106 at 156. This supports continued strong redraw after city arrival, but does not establish that noise alone causes all visible flicker.

Recommended next test, not yet rendered: preserve the low-hold branch through painting 96, use starting noise 0.25 at painting 108, then 0.10 at painting 120 onward. Keep prompts, seeds, three intervals, spatial motion and finishing unchanged. Frame 105 is a RIFE intermediate between paintings 96 and 108, so changing painting 108 also changes the interpolated frames immediately before it; retaining the old intermediates would be incorrect.

First validate the value of an earlier explicit transition-complete point. A later adaptive controller could combine a change score with confirmation that the intended scene has arrived, then apply a short settling ramp. Change magnitude alone cannot distinguish successful transformation from unwanted redesign, lighting changes or a failed transformation; a large-change trigger alone could stop a transition prematurely. No new GPU inference or controller was added in this feedback review.
