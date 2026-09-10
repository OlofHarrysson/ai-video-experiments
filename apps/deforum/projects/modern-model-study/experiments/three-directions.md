# Three directions: motion, prompt and interpolation

## Plan before execution

Olof finds both Oracle noise-0.6 recipes interesting (three sampling intervals and one interval) and agrees that nine steps at low noise did not fix flattening. He requests three bounded subagent experiments and coordination of shared infrastructure. Preserve both candidates that Olof finds interesting; no new winner is assumed.

Use the existing high3 paintings as the comparison control. Movement and prompting each change one direction independently, generating one twelve-second high3 branch with eleven recurrent repaints. Keep the same starting painting, seeds, sigma schedule, Krea weights, 24 fps, one-second repainting and default RIFE. Prompt comparison keeps the original path; motion comparison keeps the original prompt. Do not combine the two new treatments yet.

- Movement: [continuous stronger warp](motion-oracle.md). Start with a local motion-only preview and inspect deformation before new inference.
- Prompt: [simpler Oracle description](prompt-oracle.md). Reduce competing background-detail requests while preserving subject and palette.
- Interpolation: [SPEED audition](speed-oracle.md). Reuse saved paintings; exact-midpoint viability gate before a correctly timed video comparison. Preserve every endpoint, timestamp and source receipt.

Laplace owns movement code/preview, Lovelace owns the prompt runner, Sartre owns isolated SPEED setup and interpolation. The main agent owns infrastructure allocation, the shared ComfyUI queue, downloads, validation and cleanup. Agents have disjoint files and outputs. Movement and prompt use one prepared ComfyUI Pod; SPEED receives a separate GPU lease and isolated dependencies, preferably on the same Pod after ComfyUI inference. No agent independently restarts or deletes shared resources. Retain the authorized model volume.

Allocation update: two cache-region attempts failed despite a LOW availability listing. One temporary RTX4090 Pod `tl3ybyjnlc7ljr` at $0.74/hour is shared by all experiments, with container disk only. The retained EU volume is untouched; pinned Krea files and runtime are prepared on this ephemeral workspace. Allocation discrepancy logged centrally as AF-20260910-143320.

## Results

Complete. Three subagents prepared and reviewed independent directions on one shared Pod, with sequential GPU inference slots. The main agent integrated the results. No human preference for these new outputs is established yet.

| Direction | Assistant finding | Playable result |
| --- | --- | --- |
| Stronger continuous movement | Most promising: twist and expansion survive repainting, and a readable face grows out of the architecture. The 5–9s passage is strongest; by the end, expansion pushes the face toward the upper edge and a broad collar dominates. This changes composition, not just perceived smoothness. | [Current motion left / stronger motion right](../exports/motion-oracle-v001/baseline-comparison/preview.mp4) |
| Simplified Oracle prompt | Facial nose/lip forms emerge earlier, while the control retains denser ornament. Both keep fragmented eye arrangements and the amber seed. No clear evidence that simpler wording fixes temporal instability. | [Original prompt left / simplified prompt right](../exports/prompt-oracle-v001/baseline-vs-simple/preview.mp4) |
| SPEED interpolation | Some intermediate face features appear earlier, but patterned ripples and doubled contours are more visible than with RIFE. Keep RIFE for production after this bounded audition. | [RIFE left / SPEED right, matched 8 fps diagnostic](../exports/speed-oracle-v001/high3-seedface-4-5/diagnostic-8fps/comparison.mp4) |

Recommend continuing with the stronger movement, then shaping its speed/expansion to keep the most interesting composition in frame. Preserve the simpler prompt as an alternative rather than combining both changes immediately. Movement plausibly provides useful changing structure for repainting, but this single seed sequence does not establish why the face emerged more clearly.

Review evidence: subagents inspected every painting in the two new branches and fresh control, plus selected native images. Main inspected evenly sampled finished comparisons and consecutive-frame windows at 5.42–5.58s (prompt) and 8.42–8.58s (motion). The latter retains recognizable eyes, nose and collar while moving through the sampled interval. This is bounded frame-sequence evidence, not a claim of flawless playback or Olof's taste judgment. SPEED's report records all-frame diagnostic review and native crops across all three pairs.

All three individual Krea finishes and both side-by-side comparisons contain 288 frames at 24 fps, twelve seconds. Graph/feedback validation and anchor preservation passed. SPEED's three diagnostic clips retain exact endpoints and matched eighth-second samples; each is 1.125s at 8 fps, including the final endpoint display, not a replacement for the production timeline. Raw sequences, all paintings, warp-only preview and additional SPEED comparisons remain indexed in the individual reports.


## Runtime control

The first unchanged cathedral repaint on the temporary RTX4090 differs from the earlier RTX PRO4500 output: RGB mean absolute difference 1.1119/255, maximum channel difference 134. Same pinned ComfyUI source and model hashes do not guarantee byte-identical cross-runtime output. This probe does not isolate hardware from environment differences as the cause. A fresh unchanged high3 control is therefore rendered on the same Pod as both treatments, keeping the old outputs preserved. Prompt and motion comparisons use this fresh control, not the historical baseline. [Control runner](three_directions_control.py) and [review coordinator](three_directions_review.py) add this execution-specific reference without changing the independent experiment recipes. Thirty-three fresh recurrent jobs total, including the cached first prompt probe.

## Execution receipts

All 33 recurrent Krea jobs completed; requested/executed graphs, warped inputs, outputs and remote originals were downloaded. The 558-file archive passed byte-count/SHA256 verification. SPEED separately verified 29 remote files, with native output, inputs and a repeat-check image preserved. The new control and simplified-prompt first painting are pixel-identical on this runtime. Their historical counterpart was not.

The shared Pod was deleted only after both workloads' downloads were verified and the ComfyUI queue was empty. Subsequent Pod listing was empty; the authorized 50 GB EU model volume remains. Roughly twenty minutes at $0.74/hour corresponds to about $0.25 compute (estimate, not a billing receipt). The 459.73-second largest Krea download reflects the temporary uncached workspace. SPEED used a separate environment and released its GPU lease before Krea inference, allowing setup and download work to overlap without simultaneous inference or ComfyUI dependency changes.

The three original experiments and all generations remain preserved. Finishing and first-pass frame-sequence review completed locally. Archive SHA256: `f3ce4dd936b1831693b8100cb2c762708eba43f1e14ce7ffb4bbdb421729209c`. Private execution and final delivery receipts live in app-level `work/three-directions-session/`; SPEED additionally preserves its 209-artifact delivery verification in its export. No user preference for these new outputs is inferred.

## Local finishing

Use the execution-specific review adapter from `apps/deforum/`. It selects the fresh control for both comparisons, while the standalone branch helpers retain their original historical reference:

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py control build-raw
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py control prepare
# Repeat build-raw/prepare for prompt and motion.
```

Run the unchanged local `interpolate.py` pair gate and full pass on each twelve-painting `rife-sources/` directory, with source FPS 1, multiplier 24, and the inspected pair manifest supplied to `--validated-pair`. Then use `three_directions_review.py DIRECTION finish` for all three and `compare` for prompt/motion. Each final contains 288 frames at 24 fps; the final second retains native warp-only motion. SPEED uses the separately labeled 8 fps diagnostic described in its report and never changes this production timing.
