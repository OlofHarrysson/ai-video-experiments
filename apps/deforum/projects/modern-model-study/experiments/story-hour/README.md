# Deliberate movement and emerging stories

Nine recurrent Krea branches explore how spatial movement can guide a surreal journey—and how to adapt the next scene to what the model actually paints. Olof called the preceding surreal films “super cool” and authorized another hour. He explicitly welcomes backtracking and balancing artistic intention with unexpected results. His preference among these new films is pending.

**Assistant shortlist:** [Through the living book — 26⅔ seconds](../../exports/story-hour-v001/t7-through-the-living-book/faster/rife/preview.mp4) and [The clockwork world — 21⅓ seconds](../../exports/story-hour-v001/t6-the-clockwork-sun/faster/rife/preview.mp4). [Open the reviewer](http://localhost:3028/), which skips the identical first 10⅔ seconds so both new passages are easier to compare. The complete films retain that opening.

## All attempts

Original times below refer to the recorded generation timeline. Videos play 1.5× faster, at 24 fps.

| Attempt | Decision and result | Video |
| --- | --- | --- |
| T1 — Through the opening | Preserve the garden at original 16s; push toward its bright window. The smaller curved stair becomes railway sleepers and rails. A clear forward reveal, although the dominant right staircase persists. | [5⅓-second new passage](../../exports/story-hour-v001/t1-through-the-opening/excerpt-0384/rife/preview.mp4) |
| T2 — Turn and unfold | Same text, noise and seeds as T1; a much larger turn sends the opening down. Produces a dramatic diagonal railway and dark petal canopy, with a less readable destination. | [5⅓ seconds](../../exports/story-hour-v001/t2-turn-and-unfold/excerpt-0384/rife/preview.mp4) |
| T3 — Petal crosses the opening | Opposed local twists crowd the view with an orchid. The railway becomes small and peripheral. Attractive flower detail, but the motion works against the intended reveal. | [5⅓ seconds](../../exports/story-hour-v001/t3-petals-part/excerpt-0384/rife/preview.mp4) |
| T4 — Reverse the local turns | Only the two local twist signs change from T3. The opening leaves the upper edge and a perforated ivory structure dominates. This accidental wheel-like form becomes the basis for T6. | [5⅓ seconds](../../exports/story-hour-v001/t4-petals-open/excerpt-0384/rife/preview.mp4) |
| T5 — Travelling library | Continue T1's actual train painting. Paper appears first; carriage windows become reading rooms and rails become paper bridges. The wheels/supports still change abruptly, but the material connection is readable. | [5⅔-second continuation](../../exports/story-hour-v001/t5-the-travelling-library/excerpt-0564/rife/preview.mp4) |
| **T6 — Clockwork world** | Continue T4's ivory wheel toward gears, gold orbits and tiny inhabited planets. Strong surreal arrangement; the large wheel and cropped sun limit the final framing. **Shortlist.** | [Complete 21⅓-second film](../../exports/story-hour-v001/t6-the-clockwork-sun/faster/rife/preview.mp4) |
| **T7 — Through the living book** | Continue T5 through a glowing library arch toward paper trees and a distant city. The library becomes a forest threshold, with a lone traveler. This is an approach and reveal, not demonstrated continuous character travel. **Shortlist.** | [Complete 26⅔-second film](../../exports/story-hour-v001/t7-through-the-living-book/faster/rife/preview.mp4) |
| T8 — Paper forest wave | Preserve T7 through original 35.5s and add one bounded horizontal wave; text, noise and seeds stay fixed. The altered repaint inputs produce a more abstract ending and lose the clear figure. Keep T7 for the main film. | [Three-second ending](../../exports/story-hour-v001/t8-the-paper-forest-breathes/excerpt-0852/rife/preview.mp4), [matched T7 ending](../../exports/story-hour-v001/t7-through-the-living-book/excerpt-0852/rife/preview.mp4) |
| T9 — Reveal the orrery | Extend T6 with a 30% shrink and small downward shift. The sun enters view, but reflected borders become repeated gears and ribbons. Repainting does not convincingly make this a wider open scene. | [Three-second pullback](../../exports/story-hour-v001/t9-reveal-the-orrery/excerpt-0756/rife/preview.mp4) |

Comparisons: [forward versus strong turn](http://localhost:3028/story-paths), [regional directions](http://localhost:3028/story-regional), [forest endings](http://localhost:3028/story-endings), [library and pullback extras](http://localhost:3028/story-extras). The preceding shortlist remains at [surreal-hour](http://localhost:3028/surreal-hour).

## What we learned

**Give the eye a destination.** T1–T4 hold text, noise, timing and seeds fixed while changing spatial movement. Keeping the bright opening visible makes T1's reveal easier to follow. Stronger rotation is dramatic, but can move the destination out of frame or let the nearest object dominate. A motion-only preview catches that composition risk before repainting.

**Use the emerging painting to choose the next scene.** T1's train suggests repeated windows and a library; T4's ivory structure suggests a wheel and astronomical clock. These are artistic choices after inspecting the images. The later branches change both prompts and movement, so they are not controlled evidence that one recipe universally wins.

**Transformation is not the same as continuous travel.** In T7, library supports become trunks and the room opens toward a forest. The figure stays near the threshold. The result gives us a destination and a visual story without claiming a physically consistent camera or character journey.

**A local warp can change the next painting's interpretation.** T8 adds only a wave, yet its final figure becomes an abstract dark shape. Even when a bounded wave returns geometrically to zero, the intervening repaints can leave permanent changes. Editing the final video alone would not produce the same experiment.

**Zooming out needs a strategy for new space.** T9 visibly inherits the reflected border pattern. A larger generated canvas or deliberate outpainting is a future hypothesis; this session adds neither. More repainting alone did not cleanly reveal an entire new wide composition.

## Review and limitations

Main review sampled every attempt's new paintings, motion previews and selected interpolated images. Two independent reviews inspect dense frame windows: [T1 railway transition](t1-independent-review.md) and [T7 forest transition](t7-independent-review.md). Still-sequence review supports these observations; it is not a substitute for Olof's normal-speed playback judgment.

- T1 excerpt frames 32–40 contain station/carriage and track changes; 72–80 contain glass/rock changes. RIFE leaves transparent remnants.
- T5's train retains a recognizable body while paper appears, then changes more sharply into architecture around original 28.5–29s.
- T7 full-film frames 584–592 replace balcony geometry and several people with branching architecture and one traveler. Intermediate frame 588 has conspicuous overlap. Frames 624–639 offer a cleaner forest/city ending.
- T6 keeps a large foreground wheel and partly cropped sun. T8 sacrifices the readable figure. T9 retains reflected edge patterns. None establishes a general flicker fix.

Keep the accepted diffusion defaults. The strongest advance here is directing and branching around useful compositions, not a new model or sampler.

## Recurrent method and timing

All attempts use Krea Turbo, CFG1, fresh independent noise and three Euler intervals per repaint. Every new painting starts from the encoded, Lanczos-warped previous painting. Noise ramps and fixed descriptive prompt stages are recorded in [configs](configs/). RIFE never feeds back into generation.

The source timeline is 24 fps with paintings every 0.5 seconds. Delivery stays 24 fps and runs 1.5× faster: **three paintings per displayed second**, with seven RIFE 4.25 scale-1 frames between adjacent paintings. Every painting is retained. The final seven frames hold after motion settles. No delivery-speed comparison was performed.

T1–T4 each preserve 33 historical paintings through original frame 384 and add fifteen. T5 and T6 each add sixteen to their chosen parent. T7 adds sixteen to T5; T8 preserves T7 through 852 and adds eight; T9 adds eight to T6. **124 new jobs total.** The main [cut v005](../../cuts/v005.md) contains 80 paintings and 640 delivered frames. T6 contains 64 paintings and 512 frames.

`run.py` reuses the audited two-hour runner; shared code remains in `deforum_lab`. `preview.py` displays the prescribed spatial transform without diffusion. `retime.py --from-frame` supports focused review excerpts without changing generation. The shorter main-review editions omit the common opening and are checked against the corresponding full-film PNG frames.

## Verification and resources

The final local archive verifies **2,518 entries**. Generation checks validate all 124 jobs, scheduled noise/text/seeds, native graph inputs, exact warped pixels, and parent/prefix lineage. Delivery checks validate frame hashes, painting preservation, anchor timestamps, interpolation fractions and full MP4 decoding. Detailed receipts are summarized in [execution-summary.json](execution-summary.json); media and archives remain local under `exports/story-hour-v001` and `work/story-hour-session`.

One owned RTX PRO 4500 Pod at $0.72/hour served all branches. Its 248 remote media files and session scratch were removed after local verification, then the Pod was deleted. A fresh list returned no Pods; the authorized 50 GB `deforum-models` volume remains. Posted account decrease: **$0.511814111**. Conservative allowance: **$0.60**, cumulative **$3.30 of $10** across the original session and extensions. Billing snapshots and cleanup evidence are local; the allowance covers timing/storage uncertainty.

The local reviewer remains under Devrun on port 3028. All attempts and original films are preserved. Duplicate archive extraction directories were removed after their retained tar archives were hash-verified; canonical media and archives were not deleted.

Operational note: AF-20260915-132858 records a verification helper that read files before rendering completed. After completion, all nine compared pair frames and both source anchors were exact. Future consumption must wait for completed status, not only manifest-file existence.
