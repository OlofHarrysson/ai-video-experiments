# Deliberate Oracle-to-owl transition

## Accepted experiment

Olof accepts the eased-motion improvement and asks to try a deliberate subject transformation. Recognizable objects should remain legible until we intentionally transform them. The assistant selects a porcelain mechanical owl as the next subject, keeping the circular architecture, ivory/cyan/amber palette and established framing.

Preserve the accepted first eight seconds exactly. From the saved 8s painting, render two matched continuations: unchanged Oracle prompt, and owl prompt. Each receives five fresh recurrent repaints at 9–13s, followed by the usual final native hold through 14s. Source and delivery stay at 24 fps; RIFE 4.25 scale 1 connects the paintings. Spatial movement remains stopped after 8s. First visible interpolation toward the owl starts after the 8s anchor; the first owl-conditioned painting is at 9s.

Keep Krea, sigma `[0.6, 0.5128440857, 0.3109010756, 0]`, three Euler intervals, CFG1, previous-image initialization and incrementing seeds. Only positive prompt content changes between branches, besides output filenames. No reference conditioning, negative-prompt guidance, masks or copyback. The loop stays recurrent: every next repaint initializes from the immediately previous generated painting.

The [Krea author guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md), rechecked 2026-09-10, recommends natural-language descriptions and supports detailed prompts. This test describes the intended result rather than issuing editing commands. No per-frame LLM prompt expansion is used. The precise strings and schedules are preserved by the runner.

## Infrastructure

The cached EU-RO-1 region could not allocate a GPU. A PRO 6000 allocation failed despite LOW region stock; the temporary RTX4090 request also failed. A100 SXM allocated in US-MD-1 at $1.59/hour on the same pinned official ComfyUI image, with ephemeral container disk and no network mount. Both branches run on this one runtime. The retained EU model volume remains untouched. Allocation inconsistency recorded centrally as AF-20260910-174737, related to AF-20260910-143320.

## Success criteria

Look for directed replacement of human-face features by an owl's facial discs, hooked beak and feathers, while retaining readable composition and material depth. A stable old face or decorative feather-like texture alone is not a complete subject transition. Inspect original repaint anchors separately from RIFE; preserve every result regardless of outcome.

## Results

Ten new repaints completed, five per branch. Main inspected both native final paintings: unchanged Oracle text retains a human face, while the owl branch develops a hooked beak, feathered facial discs and layered ceramic feathers. The circular architecture, diagonal pose and eye locations largely persist. This is a directed subject change, not merely a feather texture applied to the old face. Independent anchor review agrees: feathers and facial discs appear at 9s, a recognizable beak develops at 10–11s, and owl markings strengthen through 13s. The inherited chrome forehead ornament persists. The two-eye portrait layout is compatible with an owl, so this is a favorable test rather than proof of arbitrary scene replacement. Finished-video review and verification are complete; see below.

The result supports separating a motion phrase from a subject transition: move and ease into a readable composition, then allow recurrent repainting to change the subject while spatial motion holds. It does not establish arbitrary object replacement, precise control over each intermediate painting or reliable negative-prompt removal. Human playback preference is still pending.

## Verification and resources

All ten jobs and 224 archive files are local and SHA256-verified. Archive digest: `938705fcdaf29e7f83ef8bf83b694d22198d6893571fb2d169fd3afb82b2a991`. The first graph took 18.121s with loading; subsequent graphs took 4.704–5.127s. The ten-job execution took 84.7s, excluding infrastructure setup, downloads, archiving and local finishing.

The temporary A100 used ComfyUI 0.34.0 and Torch 2.10.0+cu128. Its three Krea files were downloaded and hash-verified; setup is not model inference. Both experimental endings use this same runtime. The prior opening is reused exactly, rather than regenerated across GPU types.

An independent agent validated extended seeds, graph equivalence, inherited lineage, held RGB initialization and mocked actual-runner submission order before visual review. No comparison removes the feedback loop. Each repaint starts from the preceding generated painting, even after the motion stops.

Owned Pod `164r85n0147dvy` was deleted after verified downloads and an empty queue. The subsequent account Pod listing was empty. Its ephemeral container files were removed with the Pod. The retained EU network volume `vd3jnbwko1` was never attached and remains intact. Private allocation, setup, model, archive and cleanup receipts are in app-level `work/owl-transition-session/`.

## Artifacts and reproduction

- [Fourteen-second comparison](../exports/owl-transition-v001/comparison/preview.mp4): unchanged Oracle left, owl prompt right; shared first eight seconds.
- [Owl transformation](../exports/owl-transition-v001/owl/cadence-24/interpolated/preview.mp4).
- [Unchanged Oracle control](../exports/owl-transition-v001/oracle/cadence-24/interpolated/preview.mp4).
- Raw diagnostic frames, immutable anchors, actual ComfyUI graphs and feedback receipts are preserved beside the videos.

Run from `apps/deforum/`: `owl_transition.py --deployment PATH` renders ten jobs using the explicit Pod transport. The [review helper](owl_transition_review.py) supports `check`, `build-raw`, `prepare`, `finish`, and `compare`; prepare/finish optionally accept `--case oracle` or `--case owl`. After prepare, run the existing local `interpolate.py` on fourteen sources at 1 source FPS with multiplier 24, preserving the normal inspected-pair gate and RIFE settings. After finish, compare the two branches.

The manifest's inherited `graph` describes the first painting recipe; per-repaint `workflow.api.json` and `workflow.executed.json` are the authoritative prompt/seed records. The original cathedral prompt also remains in that graph and the linked source manifest.


## Finished-video review

Both individual videos are 1536×1024, 336 frames at 24 fps, fourteen seconds. The labeled comparison is 1536×554 with the same timeline. All three fully decode. Every diffusion anchor is preserved in the finished frame sequence; frames 0–192 are pixel-identical to the accepted opening PNGs. Frames 312–335 are the native final hold. The encoded MP4s are lossy; the pixel-equality claim refers to their source frame PNGs.

Main inspected the twelve-frame finished-video review: six evenly spaced samples plus six consecutive displayed frames 225–230 around 9.4–9.6s. The beak/feather transition progresses while the eyes and circular framing remain legible. A native 9.5s intermediate and the 10s side-by-side frame show an intelligible hybrid stage rather than a complete unrelated redraw. Fine details still change, and this bounded sampling does not establish artifact-free playback. Olof's response to the finished video is pending.

The comparison isolates positive scene text after the shared 8s anchor. The held spatial transform, same runtime, same seeds and unchanged diffusion/RIFE settings make directed anatomy the useful finding. Assistant recommends retaining the owl version as a complete short shot: movement, settle, transformation, brief hold. A later continuation could introduce a new bounded motion phrase after the transformation, rather than extending the same twist indefinitely. No additional experiment is started.

[Delivery checks](../exports/owl-transition-v001/delivery-verification.json), [finished-frame review](../exports/owl-transition-v001/review-finished/v001/review.json) and [independent painting review](../exports/owl-transition-v001/review-independent/) preserve the evidence. Every generation remains local; tracked code and notes reproduce the experiment, while media stays Git-ignored.
