# Rainbow Mane: opening and transformation

Status: first feasibility passage complete and screened, 2026-09-30. Olof's subsequent playback feedback: the style is pretty good, but the transformations are too abrupt. The [next study](profile-morph.md) authors a profile-to-horse drawing before testing guided repainting.

## Question

Can our recurrent Krea recipe turn a round white cartoon face into a white horse while retaining the rainbow mohawk as its mane and the supplied comic-print visual direction?

## Comparison

Screen a small opening audition. Then use one selected opening and staged scene descriptions: turn, equine transformation, pullback. Keep the established previous-image feedback, model, CFG and sampler. Record noise, seeds and camera transforms explicitly. This is directed filmmaking, not a controlled causal comparison of every ingredient.

## Cost boundary

Standing RunPod authorization in `docs/runpod.md` applies. One short-lived owned GPU, existing retained model volume, prompt and script preflight before inference. Download and hash-check all generations before removing owned compute. Do not top up the account. Current session starts with approximately $14.01 available; this is a balance observation, not a production price estimate.

## Runs and findings

Three native Krea openings are preserved and pass graph/output provenance checks. `o1-white-punk` and `o2-ink-punk` have a clear character but flatter, simpler surfaces than the references. The assistant selects `o3-comic-volume` for its violet halftone face shadow, graphic dimensional tunnel, strong white silhouette and expressive face. Its rainbow crest extends beyond the top of the close-up; the initial ease-back is intended to give it room. This is an assistant selection, not Olof's style approval.

`p01-turn-right` uses 24 paintings including the selected opening, a small leftward drift/ease-back and staged right-facing pose descriptions. The three-frame motion-only overview confirms a clear face and shows expected reflected borders in newly exposed areas; diffusion must reconstruct these. It does not predict a head turn. At painting 10 the white/rainbow identity persists, but the face remains a three-quarter view rather than a clear profile. The complete turn passage confirms this pose limitation.

All screenshots are preserved at original resolution and SHA-256 checked. Human playback judgment is pending.


## Turn and morph checkpoints

`p01-turn-right` completes 23 new paintings; the face remains a three-quarter portrait. `p01b-stronger-turn` preserves through frame 60 and changes only the repaint-noise schedule, rising from 0.82 to 0.88 before settling at 0.76. Its 18 new paintings simplify facial design without delivering a true side profile. Both complete 2.667-second comparisons are preserved with their source paintings and RIFE manifests. This bounds these prompts and noise settings; it does not prove that Krea cannot depict the requested profile.

`p02-becoming-horse` branches from the stronger early portrait at source frame 96. The first horse prompt at frame 108 immediately creates a cartoon pony: this is an abrupt semantic replacement rather than a gradual face elongation. At frame 168 a more literal horse profile replaces the exaggerated cartoon pony. The white form and rainbow hair connect the states, and frame 240 is selected for the pullback. Twelve new paintings are verified. The nine-image morph overview covers every first-transition painting (96–144), then 168, 192, 216 and 240. Precise displayed-frame inspection will follow finishing.

`p03-reveal-the-horse` begins at frame 240 with a planned fourfold pullback over five delivery seconds. The camera-only overview makes the head smaller and shifts it toward the upper right, leaving room below and to the left for a body. Reflected borders in this no-inference preview are placeholders, not generated anatomy or evidence of successful outpainting. The generated pullback completes with the horse partly concealed by a narrow doorway; the head/neck/chest remain coherent, but the intended full-body side view does not emerge.


## Selected first passage and screening

`p03b-full-body` preserves the first pullback through frame 576 (5.333 delivery seconds), then combines a stronger repaint peak (0.93–0.95) with an explicit full-body side-view description. Its 17 new paintings reveal a complete white horse with four legs and a rainbow mane/tail. This is the selected feasibility result because it reaches the requested subject and body reveal, not because it achieves the requested acting or a polished transition. All alternatives remain preserved.

The final 7.333-second, 1280×720, 24 fps export retains 66 paintings and uses RIFE 4.25 only for finishing. The first face-to-pony change at 0.875–1.000 seconds is a large replacement: an interpolated frame around 0.917 seconds shows translucent/doubled contours. Around 1.458–1.542 seconds, the pony becomes a longer equine profile, with visible facial stretching at 1.500 seconds. At 5.333–5.458 seconds the concealed frontal body becomes a full side-view horse and the setting widens abruptly; the in-betweens stretch/ghost at 5.375 and 5.417 seconds. The mane/tail carry the rainbow motif, but shape and color ordering drift. Later art simplifies and loses some opening texture. The endpoint has a clear whole-horse silhouette, not a complete plot or ending.

Inspected: eight-frame broad overviews of both complete pullbacks; every displayed frame in the shared 0.83–1.17 and 1.42–1.67 second morph windows; every displayed frame at the revised 5.25–5.58 second reveal; and a calmer comparison window at 6.50–6.75 seconds. The calmer window retains a readable horse with small redraws and camera movement. These sampled images establish specific visual defects, not the human judgment of normal-speed rhythm. Source-painted progression was additionally inspected at nine morph anchors and full-size checkpoints.

Recommendation: use this to judge the comic-print direction and the recurring white/rainbow identity. Do not extend to 30–60 seconds yet. The separate head turn is unresolved; gradual semantic morphing and the full-body reveal need better control. A pose/keyframe-guided approach is a possible next experiment, requiring a clearly agreed change to the established feedback method; it has not been implemented or validated here.

## Verification and handoff

All 118 unique generation jobs pass their configured graph, parent/input/output hashes and completion checks. All 233 owned ComfyUI input/output copies match local originals before retirement; the queue is empty, the owned Pod is deleted and its absence verified. The existing model volume remains. The selected film and both turn comparisons fully decode; source paintings and frame-role manifests are preserved. Estimated compute is recorded in [the execution summary](execution-summary.json), excluding storage and not presented as a final bill.

[Selected cut](../cuts/v001.md) · [Review](http://localhost:3028/rainbow-mane). The reviewer exposes the selected film first, with the earlier pullback and turn comparisons available in its clip selector. Olof's feedback supports keeping the visual style and improving transformation control; it does not approve the failed head turn or choose a story ending.
