# Continuous movement through the Oracle transition

Main completed the motion branch and a fresh unchanged control on the same RTX 4090 runtime. All twelve paintings per branch are local and reviewed below. Main owns raw assembly, RIFE and final video review. This worker performed no cloud action or inference submission; the frozen runner and baseline remain unchanged.

## Experiment

One new `high3` branch, changing only spatial motion relative to `exports/oracle-steps-v001/high3/cadence-24`. Same 1536×1024 starting painting (`anchors/0072.png`), Krea Turbo FP8 graph, sigma 0.6 / three intervals, CFG, matched incrementing seeds, cathedral repaint at local 1s, Oracle at 2–11s, recurrent warped-previous-image initialization, Lanczos4 reflected borders, native 24 fps and one repaint per second. Eleven inference calls; twelve anchors including the opening. The first repaint is freshly generated from the new warp, so only the opening is shared pixel-for-pixel with baseline. RIFE remains 4.25 scale 1, outside feedback. Final 11–12s uses native new-motion warps.

Sources: [runner](motion_oracle.py), [specialized review shim](motion_oracle_review.py). Outputs and all eventual run archives stay under `projects/modern-model-study/exports/motion-oracle-v001/`. Lease receipt and local mock scratch use `work/motion-oracle-session/` beneath the app root.

## Local preview and findings

[Play the matched motion-only comparison](../exports/motion-oracle-v001/motion-only/preview.mp4). Left is baseline; right is continuous motion. Both use one direct deformation of the same starting artwork per displayed frame, with no diffusion and no recurrent resampling. Comparison is 1536×554, with each artwork panel 768×512, twelve seconds and 288 native 24 fps frames. Full FFmpeg decode passed.

Reviewed six evenly spaced decoded frames, the full-size 10s frame, and all seven displayed frames from 10.75–11s. [Overview](../exports/motion-oracle-v001/motion-only/review-overview/v001/contact-sheet.jpg), [late window](../exports/motion-oracle-v001/motion-only/review-late/v001/contact-sheet.jpg). This is sampled visual inspection plus verified playable output, not a claim of normal-speed perceptual playback review.

The new view keeps winding and growing while baseline settles. The seed travels upward from the central area and leaves the frame late; the arch and patterned inner cavity continue rolling outward. No holes or folds are visible in the inspected samples. The last third stretches detail strongly: a deliberate, energetic spiral rather than a subtle increase. The generated branch must establish whether repainting restores interesting structure under this stronger travel. Do not infer diffusion or RIFE quality from this no-diffusion preview.

## Generated paintings: comparison with the fresh runtime control

**Recommendation:** audition the continuous-motion finish against the fresh unchanged control. The paintings retain the intended strong spatial travel and build a much clearer Oracle portrait, with convincing shaded volume through the final repaint. The strongest composition is around 5–9s. The last two paintings continue evolving, but become a close-up dominated by broad collar-like architecture; review the finished 9–12s passage for whether this remains engaging. This is an assistant painting recommendation, not an accepted baseline change or a playback verdict.

Main reports that the first fresh unchanged repaint on the RTX 4090 did not byte-match the historical RTX 4500 run. The correct comparator for this session is therefore `exports/three-directions-control-v001/high3/cadence-24`, rendered unchanged on the same runtime as motion. Preserve historical Oracle results as history; do not attribute differences against that older run solely to motion or assume GPU hardware alone explains the mismatch. Local manifests show twelve anchors in each new branch, 24 fps, cadence 24, 288 frames and start frame 72. Both opening files hash to `19f23dfb0d71f63532a0fc9f78ddfee528fb7c96a22f91b2ff800b41e99684d2`.

Visual evidence: inspected all 24 paintings in four matched three-time-point pages, with control left and motion right. Also opened native 1536×1024 motion paintings at 5s (`0192.png`), 8s (`0264.png`) and 11s (`0336.png`), plus the fresh control at 11s. Pages were composed in memory for inspection; no new review media or source files were written. The table records painting timestamps, not events timed from finished-video playback.

| Local time / anchor | Continuous motion | Fresh unchanged control |
| --- | --- | --- |
| 0s / 0072 | Shared cathedral opening, small orange seed in the circular cavity. | Identical opening. |
| 1s / 0096 | Seed retained; cavity and ivory arch have begun their stronger turn/expansion. | Cathedral repaint preserves the original wide composition more closely. |
| 2s / 0120 | First Oracle repaint introduces a recognizable face behind the orange seed. | Eyes appear in the ivory architecture; central seed remains separate. |
| 3s / 0144 | Face enlarges within the tilted teal opening; seed obscures its lower portion. | Architectural curls and cavities elaborate around the retained seed. |
| 4s / 0168 | Larger face and seed, with continued rotation of the enclosing rings. | One prominent eye occupies the left arch; no comparable complete central portrait. |
| 5s / 0192 | Distinct tilted porcelain face, glossy seed in front, overlapping ivory rings with fine cutouts. | Seed and receding circular architecture remain the central composition. |
| 6s / 0216 | Face and seed advance outward; eyebrows, nose and lips remain modeled rather than washed out. | Repaints refine the established eye/architecture/seed arrangement. |
| 7s / 0240 | Enlarged face keeps turning; seed travels toward the upper-left portion of the face. | Spatial path reaches its settled position; architecture still changes through repainting. |
| 8s / 0264 | Large clear portrait; the former seed now reads as a gold forehead ornament. Glossy cutout rings retain depth. | Additional eye imagery remains embedded in the architecture; seed still floats in the central cavity. |
| 9s / 0288 | Face turns toward a more upright close-up; gold ornament approaches the top edge and lower white structures expand. | Established composition persists with further surface and ornament changes. |
| 10s / 0312 | Gold form is reduced to upper crown-like fragments; the face moves upward and a large perforated collar occupies the lower frame. | Seed remains fully visible; the ring-and-eye composition is still legible. |
| 11s / 0336 | Face remains recognizable near the upper frame, with forehead cropped; broad shaded collar and cutouts dominate below. No separate orange seed remains visible. | Clear ivory lattice, turquoise insets, two architectural eyes and the central seed persist. |

**Motion retention and subject framing.** Repainting does not pull this sequence back to the original fixed composition: the central opening grows, its orientation changes across successive paintings, and the face advances toward the top of frame even after the control's path settles at 7s. This is visual evidence that the motion survives diffusion, not tracked-object proof of a rigid camera trajectory or real 3D parallax. The seed's evolution differs from the motion-only preview: it is progressively reinterpreted as a forehead/crown ornament as it travels upward. By 11s the independent orange seed is gone, while the Oracle face remains on screen. The final native 11–12s tail was not inspected in this painting review, so the exact final subject crop belongs to main's video review. Olof has already approved the strong path, including seed departure, for this GPU experiment.

**Interest, depth and detail.** At 5s, the reflective gold foreground form, shaded face behind it and several overlapping ivory rings produce a strong sense of layered depth. At 8s, coherent cheeks/nose/lips, specular highlights and dark inset cavities remain convincing at full resolution. At 11s, highlights on the face, chin/collar shading and recessed geometric openings still give volume; this does not repeat the earlier failure mode of flattening into a uniformly soft surface. Fine detail is less prominent in the very large lower collar shapes, however, and long curves/eyes are stretched by the strong deformation. The fresh control also retains depth and intricate lattice detail at 11s. Motion's advantage here is sustained compositional change and a clearer emerging portrait, not a claim that every region is sharper or more detailed. No obvious black border holes or abrupt spatial folds appeared in the reviewed paintings. Repaint flicker, doubled RIFE details, perceptual smoothness and the rhythm of the close-up cannot be judged from these anchors alone.

## Same-runtime delivery index and review handoff

Main's [three_directions_review.py](three_directions_review.py) adapter points the motion review's comparator at the fresh control. For this session use `three_directions_review.py motion build-raw`, then `motion prepare`, `motion finish` and `motion compare`, with the established RIFE step between prepare and finish. The earlier standalone commands below document the original historical-baseline handoff; use the adapter for the actual comparison.

- [Motion paintings](../exports/motion-oracle-v001/high3/cadence-24/anchors/) and [fresh control paintings](../exports/three-directions-control-v001/high3/cadence-24/anchors/) — inspected, all twelve per branch.
- [Motion raw video](../exports/motion-oracle-v001/high3/cadence-24/preview.mp4) — main owns assembly and playback verification.
- [Motion RIFE finish](../exports/motion-oracle-v001/high3/cadence-24/interpolated/preview.mp4) — main owns finishing and final video review.
- [Expected fresh-control versus motion comparison](../exports/motion-oracle-v001/baseline-comparison/preview.mp4) — emitted by `three_directions_review.py motion compare`; baseline panel is the fresh same-runtime control. Expected delivery link, not certified complete by this painting review.

For the finished comparison, inspect 1–3s for first face emergence, 5–9s for sustained reveal/depth, and 9–12s for the enlarged collar, subject cropping and moving native tail. Prefer the two-branch comparison for judging motion; keep prompt/interpolation experiments separate. Main reports 33 completed Krea jobs and 558 verified local archive files across the session, followed by Pod deletion. That cleanup statement comes from main; this worker performed no cloud-state check. At the time of the local read, the fresh control had a completed eleven-repaint verification receipt; motion's raw/review preparation was still owned by main and was not rerun here.

## Motion definition, speed and invertibility

The existing timing object retains global start time 3s (frame 72); local shot time is `u = global_seconds - 3`. The virtual coordinate system is 512×320 regardless of pixel resolution. The baseline's remaining twist ends at local 2s; its expansion ends at local 7s.

The new forward deformation `F(u)` composes localized twist then outward radial flow:

- Twist keeps baseline center `(256,160)` and radius 125 virtual units. Angular offset at radius `r` is `0.2904 u exp(-r²/(2·125²))` radians. The center-rate parameter is 0.2904 rad/s (16.639 degrees/s), exactly 1.5 times the average remaining baseline twist increment over global seconds 3–5. Tangential speed includes the spatial Gaussian and radius; the center itself does not translate.
- Expansion keeps baseline center `(220,190)` and radius 105. Its radius follows `dr/du = k r exp(-r²/(2·105²))`, with `k = 1.5·0.9/7 = 0.192857142857 s⁻¹`. This is 1.5 times baseline's average active expansion-parameter rate. Radial speed peaks at `r=105`: about 12.282 virtual units/s. At native size a virtual x unit is 3 pixels and a y unit is 3.2 pixels.
- Destination-to-source resampling for an interval `[a,b]` is `F(a) ∘ F(b)⁻¹`. This keeps the recurrent image at its actual current spatial time. No frozen end clamp or accelerated old timeline is used.

The 50% target applies to the component rate parameters, not to a uniform multiplier of screen displacement. Composition and evolving spatial gradients matter. Sampled mean one-second inverse displacement at native size is 59.92 px at 0–1s, 99.39 px at 7–8s and 153.46 px at 11–12s. Baseline is 50.11 px at 0–1s and effectively zero after 7s. The late acceleration is explicit and is a caveat for the one-branch audition.

Twist preserves radius and has determinant 1. The radial ODE has a smooth velocity field; its radial derivative is positive (`∂r(u)/∂r₀ = exp(∫v′(r)du)`), and tangential scale `r(u)/r₀` is positive. Their composition is therefore orientation-preserving for finite time. This avoids the finite-amplitude Gaussian displacement's folding limit (`1 - 2 A exp(-1.5) > 0`). Reflected border sampling is a separate image extension rule; invertibility does not mean the whole transformed canvas stays inside the original image.

Implementation uses RK4 with steps at most 1/32s on a radius grid spaced 0.25 virtual units, monotone linear lookup, and reversed lookup for the exact inverse of that numerical table. Coordinate coverage beyond radius 2048 is rejected. The reported inverse round-trip accuracy concerns the numerical table; it is not an independent ODE accuracy measurement.

## Bounded validation

`local-checks.json`: all eleven graphs match existing high3 except output prefix; 24 fps / cadence 24 / 288 frames / opening frame 72; all twelve one-second intervals have nonzero motion; baseline is stationary after 7s; identity RGB warp is pixel-exact. Forward/inverse tests and split-time spatial composition pass. Minimum sampled numerical Jacobian is 0.55291; maximum forward/inverse error is 6.15e-13 virtual units on the test grid. Geometry proof applies between samples; the discrete tests guard implementation mistakes. Screen displacement is a mapping diagnostic, not optical flow or tracked subject speed.

`runner-smoke.json`: executes the actual runner's eleven iterations with mocked file I/O and transport. Verifies each requested graph/seed, actual specialized warp and timestamp pair, source path, call count and scoped run destination. Zero network calls. This validates orchestration; real output lineage is checked after main runs inference.

The review shim replaces only the imported review module's in-process `t` binding with the new coordinate and warp functions. No shared helper file is modified. Therefore `build-raw` and `prepare` use the actual new motion, including every repaint input. `prepare` additionally verifies all actual parent-to-warp images changed. `finish` checks all twelve RIFE sources against this branch, unchanged baseline settings/code/weights, all output hashes, anchor equality and a moving native final tail. Baseline comparison reads the existing high3 finish and only writes the new comparison.

## Main-agent execution

Run from `apps/deforum/`. Main supplies its existing deployment JSON and a specific lease identifier. `render` refuses missing arguments; it creates no infrastructure. An accepted interrupted request is collected, not resubmitted; uncertain receipts remain an error for main to inspect.

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py check
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py runner-smoke
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle.py render --deployment /absolute/path/to/main/deployment.json --lease MAIN_ASSIGNED_LEASE_ID
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py build-raw
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py prepare
```

RIFE first-pair check, inspect its generated midpoint, then full run using the established local runtime:

```bash
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/motion-oracle-v001/high3/cadence-24/rife-sources projects/modern-model-study/exports/motion-oracle-v001/high3/cadence-24/rife-pair --source-frames 12 --source-fps 1 --multiplier 24 --motion-scale 1.0 --pair-only
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/motion-oracle-v001/high3/cadence-24/rife-sources projects/modern-model-study/exports/motion-oracle-v001/high3/cadence-24/rife-raw --source-frames 12 --source-fps 1 --multiplier 24 --motion-scale 1.0 --validated-pair projects/modern-model-study/exports/motion-oracle-v001/high3/cadence-24/rife-pair/manifest.json
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py finish
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/motion_oracle_review.py compare
```

Final paths: `high3/cadence-24/preview.mp4` (raw), `high3/cadence-24/interpolated/preview.mp4` (RIFE plus native final tail), `baseline-comparison/preview.mp4` (matched finishes), all under this experiment's export directory. Review generated paintings and matched 1–2s, 7–8s and 10.75–11.25s transition windows before judging the final branch. These outputs are complete. Main used the execution-specific `three_directions_review.py motion` adapter to select the fresh same-runtime control, validated recurrent inputs and anchor retention, and inspected overview frames plus consecutive frames at 8.42–8.58s. The 5–9s face passage is the preferred audition; expansion crowds it toward the upper frame later. Human playback feedback remains pending.


## Frozen remote handoff

Private session path corrected to `APP/work/motion-oracle-session` before inference. Existing preview media and receipts are preserved unchanged; the preview receipt retains the source hash from its original render. This correction changes only the lease/scratch location, not the deformation or graphs.

Main-provided deployment is supported directly:

```bash
cd /workspace/three-directions-session/app
python3 projects/modern-model-study/experiments/motion_oracle.py render --deployment /workspace/three-directions-session/app/work/three-directions-session/deployment.json --lease MAIN_ASSIGNED_LEASE_ID
```

Use main's prepared Python interpreter in place of `python3` if applicable. Runtime imports require NumPy, Pillow and OpenCV (`opencv-python-headless` suits the Pod); the repository environment also declares boto3. FFmpeg must be on PATH for the existing transport collector. The runner uses `oracle_steps.py` and its existing transitive experiment imports; include the existing app Python source tree in the bundle, retaining both modern-model-study and motion-guide-study experiment paths. There is no inference-time requirement for macOS fonts or RIFE.

Only required input media for `render` is `projects/modern-model-study/exports/oracle-steps-v001/high3/cadence-24/anchors/0072.png`, SHA-256 `19f23dfb0d71f63532a0fc9f78ddfee528fb7c96a22f91b2ff800b41e99684d2`. Finishing additionally needs the baseline RIFE receipt; side-by-side comparison needs the existing baseline interpolated frames. Those steps remain on the Mac, where the shared review harness uses Helvetica.

Archive the complete `projects/modern-model-study/exports/motion-oracle-v001/` remote directory. Fresh inference writes `high3/cadence-24/manifest.json`, twelve `anchors/{0072,0096,...,0336}.png`, eleven `warped-inputs/{0096,...,0336}.png`, eleven `anchor-{0096,...,0336}.json` lineage records, and eleven `runs/TIMESTAMP-motion-oracle-v001-high3-cadence-24-FRAME-1f/` transport archives. The lease receipt is separate at `work/motion-oracle-session/lease.json`. The runner does not build raw/RIFE frames during GPU execution.
