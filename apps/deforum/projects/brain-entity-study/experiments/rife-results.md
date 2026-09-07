# RIFE finishing comparison: P01, P03 and C02

Subsequent human review, 2026-09-07: Olof tentatively prefers **P3 + RIFE** among the continuity outputs, while finding several versions difficult to distinguish. The assistant's sampled-image analysis below predates that verdict and does not replace it. See [review harness practice](review-harness.md) for the follow-up and improved feedback process.

## Experiment written before rendering

Test whether author RIFE interpolation makes the preferred P01/P03 morphing more gradual while retaining the artwork and visible repainting. This is interpolation of preserved original PNGs, with no new diffusion, stabilization, custom motion algorithm or cloud work.

- P01: `../runs/20260907T074620462314Z-p01-guide-off-48f/frames/`
- P03: `../runs/20260907T075457156677Z-p03-cfg-45-48f/frames/`
- Each source: 48 RGB PNGs, 8 source FPS, six-second presentation.
- Deliverables: `../exports/p01-rife-24fps/preview.mp4` and `../exports/p03-rife-24fps/preview.mp4`.
- Timing: 47 pairs × three intervals + final anchor = 142 frames; append two explicit final holds for 144 frames at 24 FPS. Original frame i occupies output index 3i. Do not interpolate a repeated-frame MP4.
- First validate and inspect pair 0→1 for each source before running the corresponding 47-pair batch.
- Inspect timestamped overviews and targeted transitions using `video_review.py`. Doubled contours, disappearing holes and rubbery thin lines matter; sampled stills cannot establish normal-speed motion quality.

## Implementation selected

[Practical-RIFE](https://github.com/hzwer/Practical-RIFE/tree/bbfd2ea90910789a860ea3e2b32a240cd577b75e), pin `bbfd2ea90910789a860ea3e2b32a240cd577b75e`, supplies the MPS-compatible `model/warplayer.py`. The [author-linked RIFE 4.25 bundle](https://drive.google.com/file/d/1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg/view) supplies `train_log/IFNet_HDv3.py` and `flownet.pkl`. Its README recommends 4.25 generally; this experiment uses 4.25, not Comfy VFI's 4.26.

`../../../interpolate.py` loads that unchanged author network, strictly loads all inference weight keys (excluding the bundle's 40 `teacher.*`/`caltime.*` training-only keys), and calls the same forward path as the author's `Model.inference`: concatenated RGB tensors, t=1/3 and 2/3, scales [16,8,4,2,1]. The thin adapter avoids the training wrapper's optimizer/loss initialization and CUDA/CPU-only device selection. Padding follows the author's video runner (right/bottom zeros to multiples of 128, then crop). It omits the runner's scene/static-frame heuristics so every source pair is interpolated and every original remains intact. Float32, batch 1, scale 1, ensemble off, no compilation or automatic CPU fallback.

Local runtime, clone, downloaded bundle, weights and first-pair outputs stay in ignored `apps/deforum/work/rife-session/`. Upstream requirements were inspected: Python ≤3.11 and NumPy ≤1.23.5. Only inference dependencies are installed into a uv-created Python 3.11 environment: torch 2.11.0, NumPy 1.23.5, Pillow 12.1.0; gdown 5.2.0 downloads the author's bundle. No global installation or repository dependency/lock changes. Full resolved versions are in `requirements-resolved.txt` there.

Execution completed on 2026-09-07 on Apple M4, macOS 15.2, Python 3.11.15. No cloud resources were used.

## Adaptive C02 extension (authorized before its RIFE render)

P01/P03 completed locally with practical timings. Add C02, source `../runs/20260907T094844636087Z-c02-no-pixel-noise-48f/frames/`, as `../exports/c02-rife-24fps/preview.mp4`. A read-only comparison of the preserved workflow graphs confirms that C02 matches P03 except `/10/inputs/noise` changes from 0.025 to 0.0; the incrementing seed remains. RIFE settings and first-pair validation remain identical. This is a combined candidate for review. Compare its RIFE export with the preserved raw C02 video to isolate finishing; compare raw C02 with raw P03 to isolate pixel noise. Both earlier RIFE exports and every original remain preserved.

## Results and checks

All three outputs completed: **1024×576, 144 frames, 24 FPS, 6.000000 seconds**, H.264 CRF 18/preset slow/yuv420p, no audio. Each has 94 RIFE inferences, 48 byte-identical source anchors at indices 0,3,…,141, and two explicit final holds at 142/143. Source SHA-256 hashes and nanosecond mtimes are unchanged. Lossy MP4 encoding is for playback; byte-identical preservation applies to the exported PNG anchors.

| Export | Model setup (s) | Interpolation and PNG output (s) | Encoding (s) | Total CLI (s) | Median pair (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [P01](../exports/p01-rife-24fps/preview.mp4) | 1.11 | 12.49 | 1.93 | 16.49 | 0.255 |
| [P03](../exports/p03-rife-24fps/preview.mp4) | 1.25 | 11.89 | 1.95 | 16.03 | 0.246 |
| [C02](../exports/c02-rife-24fps/preview.mp4) | 1.07 | 11.85 | 2.26 | 16.16 | 0.245 |

Total CLI includes source inventory, hashing and ffprobe validation; dependency installation, downloads and later contact-sheet extraction are excluded. Pair timings include image loading, MPS synchronization and two PNG writes, not just neural-network execution. Padding is 64 zero rows at the bottom (1024×640 model input), removed before writing 1024×576 frames.

First-pair MPS runs were completed and their four-frame contact sheets inspected before each full batch. P01 pair: 1.50 seconds; P03: 0.32 seconds; C02: 0.33 seconds. P01 was the first successful MPS run; these are not three equivalent cold starts. Each batch requires the matching successful pair manifest and verifies its source inventory, code/weight hashes, settings and output hashes.

Six unit tests pass: original sample instants, six-second duration/holds, first-pair construction, numeric input ordering and read-only inventory, missing/duplicate indices, and mismatched dimensions (the first two timing properties share one test). Independent checks in ignored `work/rife-session/validate_outputs.py` also passed for all three: every anchor byte comparison, unchanged input hashes/mtimes, 94 intermediate PNGs each different from both of their endpoints, final hold bytes, complete MP4 decode and all decoded frame timestamps. Each decoded frame i has PTS i×512 with time base 1/12288, exactly i/24 seconds. Results are retained in `work/rife-session/independent-validation.json`.

### Setup issues resolved locally

1. Initial strict checkpoint loading rejected 40 training-only `teacher`/`caltime` keys. The author network explicitly comments those modules out; its wrapper loads non-strictly. The adapter excludes those two named groups and strictly verifies every remaining key. No inferred or random inference weights are accepted. This failed before any generation.
2. Torch 2.8.0 then failed at the author's `grid_sample` with `RuntimeError: MPS: Unsupported Border padding mode`. The failed attempt and traceback remain at `work/rife-session/p01-first-pair/manifest.json` and `p01-first-pair.log`.
3. Upgrading only torch to 2.11.0 resolved border padding on MPS. The successful pair outputs use `*-first-pair-torch211/`. NumPy/Pillow were unchanged. No CPU fallback, changed padding semantics, custom motion algorithm or cloud execution was used.

## Visual review: sampled evidence

Timestamped overview sheets are in each export's `reviews/preview/v001/`; targeted sheets and full-size decoded frames are in `v002/`. These were visually inspected, along with full-resolution P01 output 98 and P03 output 134. `review.json` records exact selections and source-video hashes. Largest-change selection used mean absolute RGB difference only as an interval locator, saved in `work/rife-session/adjacent-change-locators.json`; it is not a perceptual-quality score.

- **P01:** The overview retains the portal → mechanical head → face → landscape progression. Frames 96–99 (4.000–4.125 seconds; source 32→33) expose the hard face-to-landscape change. Frame 97 deforms the forehead/eye region; frame 98 already contains the destination scene, with a soft/doubled person and path. Frames 126–129 (5.250–5.375 seconds; source 42→43) retain warped/doubled cream contours around the central opening. These are actual synthesized frames, but not uniformly spaced semantic stages.
- **P03:** Frames 120–123 (5.000–5.125 seconds; source 40→41) stretch and dissolve the cream lower lobes while the central opening changes shape. Frames 132–135 (5.500–5.625 seconds; source 44→45) expose ghosted thin linework and a faint broad horizontal band through the cream branches in intermediate 134. The before/after anchors are sharper. Added sample count does not repair the underlying structural jump.
- **C02:** The overview retains mechanical portal detail at 1.167 seconds and branching tree/root detail near the end. At frames 117–123 (4.875–5.125 seconds; sources 39→40→41), RIFE introduces stretched outlines and partially dissolved tree/path detail. The first intermediate often remains close to its left endpoint and the second close to its right, as in the P01/P03 first-pair checks. C02 is a useful combined candidate. Its raw comparison is documented in [the continuity study](continuity.md); assess its interpolated export against that same raw C02 source before attributing an improvement to RIFE.

The P03/C02 targeted sheets show some contour blending and softening, but t=1/3 often strongly resembles the left endpoint and t=2/3 the right. Semantic replacement remains pronounced, particularly at P03 source 44→45 and the appearance of C02's tree at source frame 40. These results do not establish that RIFE produces gradual semantic morphing.

**Normal-speed playback remains required.** Only the stated sampled images were visually reviewed; full playback was not reviewed. No claim is made that these clips feel smoother, preserve the preferred repaint rhythm, or outperform their original 8-FPS sources. RIFE is now verified as a fast local finishing option; artistic acceptance remains open. Compare each interpolated clip with its own original, especially P01 around 4 seconds, P03 around 5–5.625 seconds and C02 around 4.875–5.125 seconds.

## Provenance and reproduction

Every export contains `manifest.json`, `frames/`, `preview.mp4` and two review versions. Manifests record all input/output frame hashes, absolute source paths, original mtimes, source-pair/timestep mapping, model/source/script hashes, exact commands/settings, package versions, hardware, per-pair timings, training keys excluded and ffprobe output:

- [P01 manifest](../exports/p01-rife-24fps/manifest.json)
- [P03 manifest](../exports/p03-rife-24fps/manifest.json)
- [C02 manifest](../exports/c02-rife-24fps/manifest.json)

SHA-256 receipts (observed on download, not independently publisher-signed checksums):

- Author bundle `rife425.zip`: `e63d481b7ae5d4a4e6ad7ac5b410ff78f3bf7be3b51b2e38ca8152747abde5b4`
- `flownet.pkl`: `6615790efd627772917205db291f51cd392528a157ecbb2ecaeec3bff8eb6de2`
- Author `train_log/IFNet_HDv3.py`: `655b4c772b037967b86c2dd31c8fa3b5323b79dd9a0e0088708d89149bbc8a32`
- Pinned `model/warplayer.py`: `feb3af9475b724749b023d1913c3b135431eff13d0045b8efb472a699058385f`
- Shared runner: `024ee151e79de44da0d1b5b709910f985ee5fcf98c2d7deb752878915d556d41`

From `apps/deforum/`, the successful clean setup is equivalent to:

```bash
mkdir -p work/rife-session
git clone https://github.com/hzwer/Practical-RIFE.git work/rife-session/Practical-RIFE
git -C work/rife-session/Practical-RIFE checkout bbfd2ea90910789a860ea3e2b32a240cd577b75e
uv venv --python 3.11 work/rife-session/.venv
uv pip install --python work/rife-session/.venv/bin/python torch==2.11.0 numpy==1.23.5 pillow==12.1.0 gdown==5.2.0
work/rife-session/.venv/bin/gdown 1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg -O work/rife-session/rife425.zip
unzip -q work/rife-session/rife425.zip -d work/rife-session/Practical-RIFE
uv pip freeze --python work/rife-session/.venv/bin/python > work/rife-session/requirements-resolved.txt
```

Do not rerun clone/download/extraction over the preserved session. Its existing uv environment and source/weights are ready to reuse. The exact P03 invocation was:

```bash
work/rife-session/.venv/bin/python interpolate.py \
  projects/brain-entity-study/runs/20260907T075457156677Z-p03-cfg-45-48f/frames \
  work/rife-session/p03-first-pair-torch211 --pair-only
work/rife-session/.venv/bin/python video_review.py \
  work/rife-session/p03-first-pair-torch211/preview.mp4 --overview 4 --columns 4
# Inspect the four-frame sheet before proceeding.
work/rife-session/.venv/bin/python interpolate.py \
  projects/brain-entity-study/runs/20260907T075457156677Z-p03-cfg-45-48f/frames \
  projects/brain-entity-study/exports/p03-rife-24fps \
  --validated-pair work/rife-session/p03-first-pair-torch211/manifest.json
```

P01 and C02 use their listed source paths, corresponding `NAME-first-pair-torch211` gates and `NAME-rife-24fps` export names. Outputs refuse overwrite; choose fresh output paths for another run. Original commands are retained in each manifest. The shared script has no model installer, device fallback or cloud integration.
