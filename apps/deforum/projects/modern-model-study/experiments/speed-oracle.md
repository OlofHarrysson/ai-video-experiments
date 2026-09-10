# SPEED on saved Oracle transitions

Status: **complete and verified locally**, 2026-09-10. The three comparisons contain 21 unique SPEED predictions plus one byte-identical same-seed repeat. Main agent owns infrastructure and final integration; this agent has released the GPU and has not deleted the Pod. Olof authorized the three experiment directions. Within that scope, the main agent selected and approved the exact-midpoint gate and matched 8 fps diagnostic, disclosed in commentary; Olof did not directly select 8 fps. Production 24 fps remains unchanged.

## Question and fixed inputs

Does SPEED bridge large structural changes with less doubled detail than RIFE 4.25, while preserving the endpoint paintings? Midpoint quality is the first gate; recursive consistency is a separate playback test. The source paintings remain Krea, recurrent warped-previous-image initialization, Lanczos, native 24 fps, one repaint per second. SPEED outputs never feed back into generation.

| Pair | Saved source | Shot timestamps | Reason to inspect |
| --- | --- | --- | --- |
| `high3-seedface-4-5` | `oracle-steps-v001/high3/cadence-24` | 4 → 5 seconds | Seed/face structural change |
| `high3-eye-1-2` | Same high3 branch | 1 → 2 seconds | First Oracle transition/eye |
| `high1-late-8-9` | `oracle-steps-v001/high1/cadence-24` | 8 → 9 seconds | Late high1 transition |

All input images are native **1536×1024 RGB**. Shot seconds index `rife-sources`; internal anchor filenames start at 0072 and must not be interpreted as shot-local frame numbers. The prepare command froze 27 controls (nine per pair) against the completed original RIFE receipts, verified endpoint equality, and saved original file hashes and mtimes. Baseline RIFE settings remain version 4.25, scale 1, original MPS float32 outputs.

## Exact upstream and checkpoint

Inspected the [official SPEED code](https://github.com/bbldCVer/SPEED/tree/40fadbe85c88cc6e4015062389da464fd7e85ab9), pinned at `40fadbe85c88cc6e4015062389da464fd7e85ab9` on 2026-09-10. The wrapper calls its unmodified `inference.interpolate_batch` and strict checkpoint loader. Relevant source:

- [Inference](https://github.com/bbldCVer/SPEED/blob/40fadbe85c88cc6e4015062389da464fd7e85ab9/inference.py): normalize endpoints to [-1,1], Gaussian target noise, diffusion timestep 1000, one model call, denormalize, round to uint8.
- [Model](https://github.com/bbldCVer/SPEED/blob/40fadbe85c88cc6e4015062389da464fd7e85ab9/src/models/model.py): fixed three-position endpoint/target encoding; no video-time input. Patch sizes 64/32/16; depths 2/6/4; hidden dimension 768, head dimension 64. Native source dimensions need no padding.
- [Attention](https://github.com/bbldCVer/SPEED/blob/40fadbe85c88cc6e4015062389da464fd7e85ab9/src/models/modules/attention.py): existing PyTorch SDPA path when xformers is absent. This is upstream behavior, not a local model patch.
- [Runtime](https://github.com/bbldCVer/SPEED/blob/40fadbe85c88cc6e4015062389da464fd7e85ab9/src/runtime.py): strict state-dict loading available; official checkpoint includes serialized config metadata and is loaded with `weights_only=False`.

The README's original `zhZ524/SPEED` link redirects to [bbldCVer-hf/SPEED](https://huggingface.co/bbldCVer-hf/SPEED/tree/06525dc071b4f18e822cf55d25ed6bfa858d4544), revision `06525dc071b4f18e822cf55d25ed6bfa858d4544`. `speed.pt`: **468,610,980 bytes** (469 MB decimal), LFS SHA256 `abd078f6a1135a84e13f0003e996d121d4adc2c41adf5f67d933c76c958243cd`. The model card now declares Apache-2.0; the inspected source repository has no separate LICENSE file. Model-card metadata does not establish separate source-code licensing.

## Dependencies, resource envelope and isolation

The actual inference import path needs only CUDA PyTorch, einops, OmegaConf, NumPy and OpenCV. Pillow is used for local comparison sheets. No training/evaluation imports, torchvision, diffusers, transformers, LPIPS/DISTS/PWCNet weights, CuPy or compiled correlation kernel are needed. No xformers installation is needed; its absence is asserted.

The CPU/files setup lease uses the existing image's verified Python 3.12.3 and torch 2.10.0+cu128, borrowed read-only through a separate `venv --system-site-packages` in `/tmp/speed-oracle-session`. Only missing inference libraries install into that venv; `base-environment.json`, `missing-requirements.txt`, `installed-requirements.txt` and `setup-verified.json` record actual resolution and module paths. No torch installation, ComfyUI change or system-package modification occurs. The requirements file records candidate pins for missing packages, not a demand to replace compatible image packages. CPU meta tensors count architecture parameters without allocating model weights or running GPU computations.

**Executed configuration:** one RTX4090 with 24 GB, batch one, bf16. The assigned RTX4090 had 24 GB; measured peak tensor allocation was 1,280,420,864 bytes (1.19 GiB), and peak PyTorch reservation was 1,371,537,408 bytes (1.28 GiB). These exclude driver/context and other processes; a minimum-capacity card was not tested. The wrapper records model parameter count, load time, per-call GPU-synchronized latency and peak allocated/reserved CUDA memory. Stop on OOM; no silent resize, CPU fallback or model replacement. Disk: checkpoint below 0.5 GB, frozen inputs 52 MiB, small isolated dependencies and native output PNGs. Reusing the image torch avoids downloading several GB of CUDA wheels.

Budget: initial three midpoint calls plus one same-seed repeat; after screening, eighteen remaining recursive calls give **21 unique predictions + 1 repeat** total. No inference batch larger than one. Main-agent budget is a maximum 15-minute setup/inference window; cost ceiling is the actual leased GPU hourly rate divided by four, excluding existing storage. The main agent subsequently assigned temporary Pod `tl3ybyjnlc7ljr` at $0.74/hour: 15 minutes would be $0.185 of GPU time. This agent does not allocate or delete resources. CPU/files setup is authorized separately while ComfyUI inference retains the GPU queue. Inference wrapper additionally checks `--max-calls` and elapsed `--max-seconds` before each call; an outer `timeout` enforces the whole process window. Weights may be downloaded directly from the pinned public URL into isolated scratch after lease if transferring the local verified checkpoint is slower.

## Timing contract

SPEED is **midpoint-only** here. Its `timestep=1000` means diffusion noise time, not a requested position between video frames. Recursion creates dyadic timestamps. Finite midpoint recursion cannot supply all `k/24` samples of a one-second interval because their reduced denominators can contain a factor of three. Nearest-frame selection from a 32× grid would introduce timing error, and repeating an 8× grid would introduce holds; neither is a native 24 fps reconstruction. Combining SPEED anchors with RIFE would be a separate hybrid experiment and is outside this audition.

Approved diagnostic: recurse three levels to seven new frames at exact **1/8, 2/8, …, 7/8** of each interval. Preserve original endpoints byte-for-byte. RIFE controls are read from the saved production PNGs at exact frame indices `24*start_seconds + 3*k`, for `k=0…8`. This deliberately samples RIFE at eight intervals per second; it does not claim to represent full 24 fps RIFE smoothness.

Each comparison contains **nine distinct timeline samples at 8 fps**. Relative endpoint PTS are exactly **0 and 1 seconds**. Total container duration is **9/8 = 1.125 seconds** because the final endpoint is displayed from **1.000 to 1.125 seconds**. Both methods have identical sample timestamps, duration and final endpoint display. There are no silently repeated or discarded diagnostic samples. The frame labels and receipts explicitly state 8 fps diagnostic, endpoint timing, final display interval and unchanged production 24 fps. Native PNGs are preserved; the side-by-side presentation alone uses Lanczos downscaling to 768×512 per method.

Seeds are deterministically derived from base `20260910`, pair ID and reduced rational target timestamp using SHA256. Recursion order does not change the seed of a node. Every node records seed, exact target/parent fractions, input/output hashes and measured latency. Recursion uses saved uint8 PNG outputs as parents; this quantization boundary matches the upstream image I/O path. Same-seed midpoint repeat must be byte-identical on the same runtime/GPU. This is not a cross-device reproducibility guarantee.

## Commands and local artifacts

Run from repository root. The local prepared work directory is `apps/deforum/projects/modern-model-study/work/speed-oracle-session/`; it has a scoped `.gitignore` because the root ignore rule only covers app-level work directories. Its `SPEED/` checkout, setup script, requirements, weights and frozen input bundle are ignored. The tracked additions in this scope are this note, `experiments/speed_oracle.py` and `work/speed-oracle-session/.gitignore`; the latter excludes all work contents except itself.

```bash
apps/deforum/work/rife-session/.venv/bin/python apps/deforum/projects/modern-model-study/experiments/speed_oracle.py prepare
apps/deforum/work/rife-session/.venv/bin/python apps/deforum/projects/modern-model-study/experiments/speed_oracle.py self-test
```

For the main agent: copy the **whole isolated session directory** (excluding partial weights and any local venv) plus the exact `speed_oracle.py` into the leased scratch directory. Commands below are relative to that remote session directory. `LEASE_ID` must identify the explicit main-agent lease; merely setting a string does not create authorization. The runner itself has no network or cloud-control code.

```bash
# Within main-granted lease only; log stdout/stderr and enforce remaining budget.
timeout 300 bash setup-isolated.sh
# First gate: exact midpoint from three pairs + identical-seed repetition.
timeout 600 .venv/bin/python speed_oracle.py infer \
  --bundle bundle --upstream SPEED --weights speed.pt --output results \
  --lease-id LEASE_ID --depth 1 --max-calls 4 --max-seconds 540 --repeat-check
# After midpoint screening and with time still inside the same overall lease:
timeout 600 .venv/bin/python speed_oracle.py infer \
  --bundle bundle --upstream SPEED --weights speed.pt --output results \
  --lease-id LEASE_ID --depth 3 --max-calls 18 --max-seconds 540
```

The separate timeout values are per-command upper bounds, not permission to extend the main agent's 15-minute total window. For copying results home, place the contents of `results/` directly in project `exports/speed-oracle-v001/`. Preserve `inference.json`, endpoint PNGs and every output, including failed/partial attempts and repeated midpoint. Then build midpoint sheets first and video only once seven recursive predictions exist per pair:

```bash
apps/deforum/work/rife-session/.venv/bin/python apps/deforum/projects/modern-model-study/experiments/speed_oracle.py compare
apps/deforum/work/rife-session/.venv/bin/python apps/deforum/projects/modern-model-study/experiments/speed_oracle.py compare --video
```

Expected outputs per pair: `midpoint-comparison.png`, native `speed/*.png`, `diagnostic-8fps/comparison.mp4`, its nine numbered presentation frames and a timing/hash/ffprobe receipt. The encoder checks all nine decoded PTS, 8 fps, 1.125 s duration, both original endpoints and full ffmpeg decode. Use `apps/deforum/video_review.py` for a bounded nine-frame overview, then inspect selected native crops. Do not claim playback quality from the midpoint sheet alone.

## Verification and findings

- Prepared all three requested source pairs and 27 exact-time controls; frozen input manifest SHA256 `74c0de31c3cb533cde125427b4f7a4236bbb63f2187cf67fdabadecc695e32ec`.
- Local self-test passes: recursion parents exist before children, exact eighth timestamps, inability to obtain 1/24 from this recursion, stable distinct node seeds, all input hashes and original source mtimes preserved.
- The official checkpoint is downloaded locally and its full byte count and SHA256 match the pinned Hugging Face LFS metadata.
- Both granted GPU sessions completed: four first-gate calls and eighteen remaining recursive calls, no OOM. All 29 remote result files (28 PNGs plus inference receipt) matched the remote SHA256 inventory and are local. GPU lease `speed-oracle-001` was explicitly released before local finishing.
- Every comparison fully decodes and has nine frame PTS at exact 0, 1/8, …, 1 seconds, 8 fps and 1.125 s duration. Six original endpoints remain byte-identical.
- Reviewed every decoded frame in all three clips using `video_review.py`, plus native midpoint and 0.25/0.5/0.75-second crops. This is complete frame-sequence evidence, not a human playback preference or a production24fps smoothness result.
- The review reader initially rejected the custom receipt because it lacked its expected `output_frames` fields. Added the verified paired sample roles/times in this experiment's presentation metadata; no video pixels, timestamp, inference result or shared review code changed. The exact executed inference runner is preserved as `exports/speed-oracle-v001/provenance/inference-runner.py`; the current source additionally emits compatible review metadata.

## Result and recommendation

**Keep RIFE 4.25 scale 1 for production.** SPEED runs cheaply and can introduce intermediate face features earlier, but this recipe did not produce a convincing overall quality win on the three saved pairs. The clearest new artifact is a fine patterned ripple/ghost contour on otherwise clean painted surfaces and rail edges. No broader model-capability conclusion follows from three cases and one fixed seed per node.

| Pair | Frame-sequence and native-detail finding | Comparison |
| --- | --- | --- |
| Seed → face, high3 4–5 s | SPEED shows an eye at relative 0.25 s and more face semantics at 0.5 s. RIFE remains cleaner and reaches a readable face by 0.75 s. SPEED adds striped/rippled orange surfaces and duplicate rail contours. | [Playable matched 8 fps](../exports/speed-oracle-v001/high3-seedface-4-5/diagnostic-8fps/comparison.mp4), [native detail](../exports/speed-oracle-v001/high3-seedface-4-5/detail-sequence.png) |
| Eye transition, high3 1–2 s | Most obvious regression: stippled/rippled dark holes and turquoise ring edges at 0.25/0.5 s. RIFE keeps cleaner shading. No clear improvement in the larger motion. | [Playable matched 8 fps](../exports/speed-oracle-v001/high3-eye-1-2/diagnostic-8fps/comparison.mp4), [native detail](../exports/speed-oracle-v001/high3-eye-1-2/detail-sequence.png) |
| Late high1 8–9 s | Closest at overview scale. SPEED still softens/displaces rail and hole edges slightly; no compelling advantage. | [Playable matched 8 fps](../exports/speed-oracle-v001/high1-late-8-9/diagnostic-8fps/comparison.mp4), [native detail](../exports/speed-oracle-v001/high1-late-8-9/detail-sequence.png) |

Measured on the assigned RTX4090, native 1536×1024, batch one, bf16, upstream SDPA:

- Model: **117,131,648 parameters**, strict checkpoint load; zero missing/unexpected keys.
- Unique-call median **0.0950 s**, range **0.0781–0.4037 s**; the 0.4037 s call was the first. Per-call timing includes inference and conversion back to host RGB, excludes file writing.
- Two process runtimes total **14.5717 s**, including two approximately 3.45 s checkpoint/model loads. This excludes setup, transfer, review and other Pod usage, and is not a billable session-cost report.
- Peak allocated **1.19 GiB**, reserved **1.28 GiB**; no OOM. Same-seed repeat is byte-identical.
- Only OmegaConf 2.3.0 and antlr4-python3-runtime 4.9.3 were missing and installed in the isolated venv. Borrowed image versions: Torch 2.10.0+cu128, OpenCV 4.13.0, einops 0.8.2, NumPy 2.5.0, Pillow 12.2.0. No GPU environment packages were replaced.

The seedface comparison is the most useful single clip to show the tradeoff. The eye comparison is the meaningful contrary case. Preserve all three; Olof's playback verdict is pending. No new experiment or 24 fps hybrid reconstruction is authorized by this note.

## Shared-workspace handoff

All paths are in the shared `/Users/olof/git/ai-video-experiments` checkout. Main agent owns final integration, commits and shared indexes; this agent did not edit shared files or commit/push. The scoped `.gitignore` alone was staged as requested so the ignored work rule is tracked; the runner and report remain new files for main-agent integration.

- Runner: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/modern-model-study/experiments/speed_oracle.py`
- This report: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/modern-model-study/experiments/speed-oracle.md`
- Versionable work ignore file: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/modern-model-study/work/speed-oracle-session/.gitignore`
- All delivery artifacts: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/modern-model-study/exports/speed-oracle-v001/`
- Isolated setup/work/verified checkpoint: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/modern-model-study/work/speed-oracle-session/`

The export contains native predictions/endpoints/repeat, three H.264 comparisons, every presentation and decoded review frame, midpoint sheets, native detail sequences, the self-contained 27-image `input-bundle/`, `summary.json`, `download-verification.json`, timing/encoder manifests, inference receipt, exact executed runner and source snapshot, setup/requirements logs, and remote SHA256 inventory. `provenance/upstream.tar.gz` also preserves macOS AppleDouble sidecars that appeared in the original source-hash inventory during transfer; they are not imported Python modules. All inventoried source bytes match. The current runner excludes those metadata sidecars from future code inventories, and adds review-compatible presentation metadata; use the archived exact runner if resuming the original inference receipt without an identity mismatch.

No remote SPEED result is needed anymore. The main agent has been told downloads are verified and can delete its Pod once its own experiments are secure. This agent did not modify ComfyUI, restart services, allocate resources or delete the Pod.

Final local delivery verification passed: **209 indexed artifacts**, with all remote result hashes, all endpoint/diagnostic-frame hashes, every exact eighth timestamp, three decoded review/video bindings, and the frozen source/runtime provenance checked. `exports/speed-oracle-v001/delivery-verification.json` records the inventory. Recheck with `apps/deforum/work/rife-session/.venv/bin/python apps/deforum/projects/modern-model-study/work/speed-oracle-session/verify_delivery.py` from the repository root; this is local-only and submits no inference.
