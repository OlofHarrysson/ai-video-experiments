# One hour of stronger spatial motion

Olof finds the previous two films quite nice but too static. He wants more readable panning, zooming and spatial warping. This extension runs from approximately 18:22:32 to 19:22:32 UTC on 2026-09-14. Finish already-started work afterward if necessary; keep this extension plus the preceding session within $10 total. Preserve all attempts and the recurrent Krea feedback loop. Final deliveries remain 24 fps with RIFE; preview the underlying motion before repainting.

## What to watch

Assistant shortlist: **[Porcelain — travelling twist, 9⅓s](../../exports/motion-hour-v001/m2-travelling-twist/faster/rife/preview.mp4)** and **[Malachite — through the gap, 8s](../../exports/motion-hour-v001/m6-steer-through-gap/faster/rife/preview.mp4)**. These are candidates for Olof’s playback feedback, not new selected defaults. The faster versions keep every diffusion painting and recompute fewer intermediate frames; all output remains 24 fps.

[Open the two-film reviewer](http://localhost:3028/). Other comparisons are separated to keep the main choice manageable: [three spatial paths](http://localhost:3028/motion-paths), [forward zoom versus steering](http://localhost:3028/motion-travel), and [the same twist at two speeds](http://localhost:3028/motion-pace). The [previous two-hour shortlist](http://localhost:3028/two-hour-lab) remains available.

| Attempt | What changed | Finding |
| --- | --- | --- |
| [M1 · broad sweep](../../exports/motion-hour-v001/m1-sweeping-camera/finish/rife/preview.mp4), 14s | Larger pans, zooms and broad turns | Clearer movement, especially the first 5.5s; later framing is cramped and reflected edges intrude. |
| [M2 · travelling twist](../../exports/motion-hour-v001/m2-travelling-twist/finish/rife/preview.mp4), 14s | Strong local turns around moving centres | Strongest porcelain composition change: upright curl, opening folds, then cranes. Ghosting remains in the crane transformation. |
| [M3 · elastic wave](../../exports/motion-hour-v001/m3-flowing-wave/finish/rife/preview.mp4), 14s | Horizontal bands sway differently | Distinct flexible motion, strongest at 5–7s. Stretched silhouettes and late edge repetition make it a secondary option. |
| [M4 · forward travel](../../exports/motion-hour-v001/m4-malachite-run/finish/rife/preview.mp4), 12s | New layered passage and 4.35× cumulative zoom | Readable forward movement and mineral-to-canyon color/material change. A large leaf stays in the way. |
| [M5 · stronger zoom](../../exports/motion-hour-v001/m5-malachite-surge/finish/rife/preview.mp4), 12s | Same recipe, 7.69× cumulative zoom | Exposes more canyon but also enlarges the leaf. Strength alone does not choose a useful destination. |
| [M6 · steer through gap](../../exports/motion-hour-v001/m6-steer-through-gap/finish/rife/preview.mp4), 12s | Preserve M4 through 6s, then aim toward the stream | Leaf shifts right; the river and distant basin become more readable. Near surfaces still grow large. |
| M2/M6 faster editions, linked above | Preserve all 28/24 paintings; compress their time by 1.5× | More active pace without new diffusion. Transition artifacts remain; speed is not a repair. |

The practical lesson is to give movement a destination and a bounded duration. Stronger warping makes composition change clearer, but it can also crowd the frame or amplify border defects. Steering into visible open space worked better in the malachite example than simply increasing zoom. Recurrent repainting is still connected throughout; neither RIFE nor independent redraws replace it.

Motion-only previews are preserved under [the export’s motion-only folder](../../exports/motion-hour-v001/motion-only). M6’s continuation preview starts from the actual six-second painting; it is not a full-film preview. The small-pan draft is also preserved. No depth, optical-flow estimator, new model, custom ComfyUI node or image blending was added.

## First round

Reuse Porcelain Weather's exact opening, prompt stages, noise curve, painting times, seeds and three-interval Euler/CFG1 recipe. Restart from frame zero, changing only the motion path. Each fourteen-second branch has 27 new paintings.

- Sweeping camera: substantially larger zooms and pans, with broad turns and changes of direction. Positive zoom creates some room for panning; it does not guarantee artifact-free borders.
- Travelling twist: stronger localized turns around changing centres, alternating direction so the whole scene does not wind up around one point indefinitely.

The existing fourteen-second stronger-transformation version is the historical baseline. Inspect direct motion previews and recurrent raw paintings separately. Large movement may expose reflected borders, make RIFE struggle or be partly undone by repainting. Measure/observe those effects before interpreting the outcome as a motion-control success. The shared runner is reused through an explicit experiment path adapter; no diffusion graph or dependency change is intended.

## Travelling wave control

A third matched branch adds an invertible horizontal shear wave: x displacement varies sinusoidally with y and time, while y is unchanged. A smooth envelope brings it back to zero at either end of each phrase. It combines opposite movement in different image bands with a mild zoom and pan. This is direct mathematical motion; no optical-flow or depth model is added. Forward/inverse tests include composition with the existing twist/zoom transform and exact identity outside the wave interval. All historical motion paths retain their existing branch. Preview the motion before submitting this branch.

Motion-only review: the camera branch has substantially closer framing and a tilting horizon, while the strong twist carries the wave upward and leaves more empty space late. Keep that as an explicit deformation stress case. The travelling wave bends the wave face and slides image bands back and forth while broadly retaining the initial framing; no major empty border was visible in the sampled preview. These previews sample the original image through the cumulative mapping at each time, rather than applying repeated image resampling or diffusion.

## First repainted camera result

All 27 new paintings and 472 archive files are local and verified. The stronger global path changes framing substantially: the wave fills the frame by 2–4s, a large paper overhang dominates by 8–9s, and cranes appear amid the closer paper forms. Fine grain and reflected edge patterns remain at the low-noise ending. The first RIFE interval was inspected at frames 0/3/6/9/12 before full finishing; its modest initial zoom appears coherent. Later high-motion intervals still require targeted review. The twist/wave comparison is rendering on the same prepared GPU.

## The Malachite Run

Implement the independent [forward-travel proposal](forward-shot-plan.md): a new twelve-second mineral passage → violet jungle → vermilion canyon. The opening is generated by Krea before any feedback. Use the proposed 4.35× cumulative forward magnification with alternating lateral weave and a mild travelling wave. Repaint every half second; use an authored noise rise for each environment change, then settle to 0.25. This creative application changes composition, prompts and motion together, so it is not a causal comparison with the porcelain cases. Screen the opening and motion-only preview before recurrent rendering.

## Stronger forward scale

The new opening has readable near mineral arches, smaller openings behind them and a central silver stream. Its motion-only preview keeps the destination visible while the first arch moves outside the frame. Add a matched surge branch that uses the same opening, prompts, seeds, noise and timing but multiplies each positive zoom amount by 1.5, increasing cumulative magnification from about 4.35× to 7.69×. This tests stronger forward travel without increasing the sideways bend or repaint strength. Inspect its motion preview before painting.

## First matched motion comparison

The M1/M2/M3 archive contains 1,357 verified files, including the separate new opening. Raw M2/M3 paintings were inspected at 0/2/4/6/8/10/12/13.5s. The localized twist makes the largest readable composition change: the wave rises almost vertically, folds aside, then opens a gap for cranes. The travelling wave produces a more elastic back-and-forth motion while retaining the curling silhouette longer. Reflected edge patterns and late grain remain. The first RIFE pair of both was reviewed at 0/3/6/9/12 before full finishing.

Measured geometric displacement of a fixed image grid per half-second interval has median 18.7px for the prior R7 path, 31.6px for M1, 57.3px for M2 and 46.5px for M3 at 1536×1024. These are prescribed mapping values, not observed optical flow or perceived-motion ratings. The largest motions also send a small part of the grid outside the image.

The large archive SCP transfer stopped progressing at 58,229,760 bytes while other SSH commands worked. A checked byte-offset resume over SSH completed the file; full archive SHA and every inventory entry passed before restoration. Root cause remains unverified. Incident AF-20260914-205037 preserves this operational issue.

The first malachite result visibly travels into the opening and converts green mineral surfaces to orange canyon walls. It retains an oversized violet leaf in the middle through the ending, narrowing the intended view into the basin. This is an observed composition limitation, not yet evidence that stronger zoom will solve it.

## Steer through the visible gap

M4 retains the large violet leaf at the centre, so a bounded follow-up preserves its exact first six seconds and adds an off-centre push toward the visible stream left of that leaf. It adds 1.9× forward scale and a rightward image displacement during 6–11.5s, allowing the leaf to leave the centre. Prompts, noise, seed schedule and repaint timing remain identical. This tests choosing a useful destination in the image rather than only increasing global zoom. Preview from the actual six-second painting before rendering eleven new repaints.

## Faster delivery from all the same paintings

After screening the matched motion results, make a 1.5× speed version of M2. It retains all 28 paintings in their exact order, moves their timeline positions from 0/12/24… to 0/8/16…, and recomputes RIFE for those exact one-eighth intervals. Working inference remains recorded on the original timeline; delivery stays 24 fps and lasts 9⅓ seconds with three paintings per displayed second. No diffusion jobs are added. The original fourteen-second output is preserved. The first interpolation pair is inspected before the complete retime, and a separate verification confirms every painting hash, timeline position and intermediate fraction.

## Review notes and current interpretation

[Independent M1 review](m1-review.md) favours the opening 0–5.5s, with cramped framing and reflected borders later. [Independent M3 review](m3-review.md) identifies 5–7s as the clearest elastic movement, while the crane transition at 8.625–8.875s has major translucent overlap. These are ordered-frame inspections, not human playback choices.

Main-agent M2 review includes raw paintings through 13.5s and RIFE frames 84/87/90/93/96/99 and 192–225 at three-frame increments. The upright curl and its unfolding are readable; the crane transition still has considerable ghosting at 8.625–8.875s. The 1.5× retime retains the same failure over a shorter displayed interval; it is a pacing option, not a repair.

M4 and M5 share all non-motion settings. M5 enlarges the foreground faster and exposes more orange canyon by 8–10s, but the violet leaf remains dominant. M6 preserves the exact M4 prefix through 6s and steers into the stream opening; raw 8s and 9.5s show a substantially clearer river route with the leaf displaced right. Choosing the destination has more practical value here than increasing the zoom coefficient alone.

## Eight-second travel option

Apply the same 1.5× delivery retime to M6 after its full archive is verified. It retains all 24 paintings, including the preserved opening, and places them at eight-frame intervals in a 192-frame/24 fps video. The original twelve-second film remains available. Treat the shorter version as a pace audition; it does not change any image-model output or repair its interpolation artifacts.

## Delivery and cleanup

All 139 new image jobs pass graph, execution, warped-input pixel and recurrent-parent checks. The final local archive contains 2,305 SHA-verified entries; its SHA-256 is `5f9062fb9b2903462d9c3ef329902a8d37592fbebf488ad64b0046abc06c8dc5`. Checks also confirm identical non-motion settings within the porcelain family and within the malachite family. M6 preserves the M4 paintings through frame 144.

All six original deliveries and both faster editions pass complete decoding, frame counts, anchor hashes/timestamps, final holds and RIFE 4.25/scale1 verification. The eight videos contain 2,288 delivered frames in total. Original painting records remain on their generation timeline; retiming has separate provenance. The wave transform passes composition/inverse and endpoint/row-direction tests; changed Python scripts pass Ruff. No runtime or model dependencies changed.

The owned `deforum-motion-hour` Pod was deleted at approximately 19:08:23 UTC after local verification and removal of 277 owned ComfyUI media files and session scratch. A fresh listing has no Pods. The authorized 50GB `deforum-models` volume remains in EU-RO-1. Incremental posted account debit: **$0.55635**; conservative allowance **$0.60**. Combined with the preceding session’s $1.45 allowance, this is **$2.05 of the original $10 limit**. The ongoing retained model volume remains a separate authorized cost. No new credentials or account changes were needed.

Local evidence: `work/motion-hour-session/session.json`, archive receipts, cleanup receipt and bounded review sheets. Media manifests and delivery checks live with each export. The local reviewer remains running for Olof through Devrun service `media-review`; cloud compute is off.

Final visual review also sampled M4/M5 interpolation at 6.75/7.75/8.75/10.25s and M6 at 6.25/6.75/7.25/7.5/7.75/8/8.25/8.5s plus later midpoints through the final hold. The faster M6 received additional samples at frames99/105/111/117/123/153, including newly calculated interpolation fractions. Canyon conversion has translucent contours and temporarily softer mineral bands, but the later river opening remains readable. The shortlist recommendation is based on those bounded sequences, raw painting progression and browser playback checks; Olof’s preference remains unconfirmed.
