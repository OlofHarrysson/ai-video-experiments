# Continuous movement and a wider motion palette

2026-09-15. Olof likes the imagery but finds the spatial transformations repetitive and notices stops. This hour targets continuous slow-to-fast movement, combining pans, inward/outward zoom, local spirals, waves, shear and flat-sheet plane turns. Storage work is deferred until pressure returns.

The [motion palette](../../../../../../docs/motion-palette.md) links artistic intent to supported controls and distinguishes browser demonstrations from integrated recurrent effects.

## Frozen first comparison

- C3 Banking Voyage: underlying diagonal travel, banking spiral, sideways plane turn, pullback, vertical travelling bend, then a different tilt and local turn.
- C4 Folding Worlds: pull back first, tip the sheet on two axes, shear its upper/lower areas, enter a spiral, carry a horizontal wave, then bank into another perspective change.

Both preserve the same pomegranate opening and F3's complete prompt/noise/seed schedule. CFG1, Krea Turbo, three Euler intervals, recurrent warped-image initialization, independent noise, Lanczos, half-second source repaints and RIFE remain unchanged. Source is 24 fps; the established 1.5× finish delivers 24 fps and three paintings per displayed second. C1/C2 are gentler motion-only design drafts, with no paid inference.

The new `cruise` transform carries an underlying velocity through eased phrase transitions. Plane transforms project a flat sheet, not a depth-estimated scene. Their composition and exact inverse are tested, along with timebase independence; historical phrases retain their prior behavior. The frozen C3/C4 paths have no zero in the sampled median viewport movement, but this is not proof of perceptual continuity after repainting and RIFE.

## Session

Start 19:58 UTC; no new experiments after 20:58 UTC. This hour remains within the original $10 maximum, with $3.95 conservatively allocated beforehand. The owned RTX PRO 4500 Pod was deleted at approximately 20:36 UTC, after its 236 input/output media files were hash-checked against the downloaded archive and removed. The shared model cache remains.

Posted account debit at cleanup: **$0.370355**. Allow **$0.45** for this session including disk/billing timing, giving a conservative cumulative **$4.40/$10**. The account then showed no Pods and $0.005/hour for retained storage; this is not a zero-spend account. All finishing runs locally on the Mac.

## Results

Human feedback on these new films is pending. These are assistant selections based on paintings, representative finished frames and denser transition windows.

| Attempt | What changed | Observation |
| --- | --- | --- |
| C1/C2 motion-only drafts | Gentler paths on the original image, without diffusion | Helpful to expose a near-cancellation of movement; amplified before paying for inference. Preserved as design drafts. |
| [C3 Banking voyage](../../exports/continuous-motion-hour-v001/c3-banking-voyage/faster/rife-moving-tail/preview.mp4) · 16s | Continuous drift plus spiral banking, plane turns, pullback and a vertical bend | Preferred of the two matched routes. Strong diagonal passage through the city and palace-fish, with a readable orchid railway. Still has large open blue areas and a crowded late flower. |
| [C4 Folding worlds](../../exports/continuous-motion-hour-v001/c4-folding-worlds/faster/rife-moving-tail/preview.mp4) · 16s | Identical generation controls; pullback, two-axis plane tilt, shear and a different spiral/wave route | A clearly different composition, useful as a motion comparison. Earlier pullback exposes more repeated/mirrored forms; the ending is crowded. |
| [C5 Under the orchids](../../exports/continuous-motion-hour-v001/c5-under-the-orchids/assembled/preview.mp4) · 24s | Continue C3 from its last painting; steer under the orchid toward the visible train and describe rails becoming strings/harps | Stronger visual story: railway becomes harp-like bridges. Continuous movement remains visible through the final warp frames. The intended wide harp-island vista does not fully appear; foreground scrolls crowd the ending and become more illustrative. |
| [C3 with motion separated during finishing](../../exports/continuous-motion-hour-v001/motion-aware-full/explicit-motion/preview.mp4) · 16s | Exactly the same 48 paintings; align, interpolate, then apply the prescribed spatial movement | Promising reduction in doubled architecture and seed details during turns. Orchid sections are more similar. This is an optional finishing candidate, not a proven universal smoothness fix or a changed diffusion default. |

The root [reviewer](http://localhost:3028/) compares C3/C4. [Complete film](http://localhost:3028/continuous-film) shows C5. [Finishing comparison](http://localhost:3028/continuous-finishing) shows identical C3 paintings with the two interpolation methods. [Previous round](http://localhost:3028/fluent-hour) remains available.

## What we learned

**Keep a base movement through changes in emphasis.** Easing every transform to rest can make a film repeatedly pause. A small persistent drift allows larger turns, pushes and pullbacks to accelerate/decelerate while something keeps moving. Overlap and inspect the combined movement: independent effects can cancel each other, and nonzero geometric velocity does not ensure a visibly fluent finished shot.

**Change the kind of movement, not only its strength.** The matched C3/C4 configurations differ only in `case` and `phrases`. Their different compositions therefore demonstrate a useful expanded motion palette, without a concurrent prompt or diffusion change. Flat-sheet projection supplies asymmetric size/motion across the image; it is not reconstructed 3D geometry.

**Choose the next destination from the painting.** C5 responds to the actual train under the orchid. Linking rails to strings gives the next transformation a visual connection. Pulling out further does not automatically produce an uncluttered scene: repeated foreground structures still need composition decisions.

**RIFE can be asked to solve a smaller problem.** The local finishing candidate first warps the right painting backward to the left painting's coordinate frame, interpolates that aligned pair, then warps each intermediate result forward along the recorded motion. Original diffusion paintings are copied unchanged at their timestamps. The new process adds resampling and border exposure; it still relies on RIFE for changes in content and cannot eliminate an abrupt repaint. It never feeds into recurrence.

## Evidence and reproduction

- **118 new image jobs:** 47 C3 + 47 C4 + 24 C5. The shared opening and C5 prefix are preserved. Generation checks reproduce every saved warped input exactly from the previous painting and verify its job output. All three controls retain CFG1 and the existing noise/prompt schedules except C5's explicitly extended scenes.
- The complete downloaded archive contains **1,989 verified files**, SHA256 `26718ca8ba57a0d18809423f206321c2edcfc5e9ecdd99c031ac5bfd4098d2b4`. It includes the actual remote source bundle, configuration and execution records. Local `work/continuous-motion-session/` retains download verification, billing and resource-cleanup receipts.
- Deliveries are 1536×1024 at 24 fps: C3/C4 have 384 frames and 48 paintings; C5 has 576 frames and 72 paintings. Each has seven actual spatial warps after the final painting and no final hold. Video decoding and frame hashes are checked. C5 preserves C3's first 376 finished frames, then includes the shared last painting as its continuation's first frame.
- The finishing diagnostic checks all 47 aligned inputs, pinned RIFE source/weights, all 48 unchanged paintings, identical direct-control frames and identical seven-frame tails. Its short eight-pair screen is also preserved under `motion-aware-probe/`.
- Review sheets live under `exports/continuous-motion-hour-v001/review/` and `motion-aware-full/comparison-*.jpg`. Sampled finished windows include frames 64–72, 160–168, 248–256 and 352–360; C5's ending is inspected densely through frame 575. These samples support the observations above, not a quantitative perceptual-quality score.
- **69 unit tests pass**, including six motion tests. Production-size projection, exact inverse composition and timebase independence are covered. Historical F3 maps remain unchanged.
- Devrun reports the local reviewer ready, and all four current/previous served pages match the built files by SHA256. Chrome attachment timed out twice, so the final browser rendering was not inspected this turn; refresh the existing tab to load the new data. The UI code and layout are unchanged. Tool friction AF-20260915-224533 records that limitation.

Run from `apps/deforum` using `uv run --locked python projects/modern-model-study/experiments/continuous-motion-hour/<script>.py`. `run.py` reuses the established recurrent runner; `preview.py` renders motion alone; `retime.py`, `moving_tail.py` and `assemble.py` finish and preserve paintings. `motion_aware_probe.py` has separate `prepare`, `infer`, `compose` stages and `--full`. `verify_finishing.py` audits that candidate; `build_reviews.py` rebuilds the review pages. Generation and finishing scripts reject overwriting completed outputs; choose a fresh case for new artwork.

## Runtime check

The first 1536×1024 local verification exposed a NumPy batched-matrix-multiplication segmentation fault on macOS; smaller previews had passed. The plane projection now uses an explicit `einsum` contraction with BLAS optimization disabled. All 47 C3 warped inputs then reproduced the Linux render inputs **pixel-for-pixel**, and the full generation provenance check passed. Six focused motion tests now include production-size projection. This resolves the observed operation failure without claiming a root-cause repair of NumPy itself; friction record AF-20260915-222200 preserves the incident.
