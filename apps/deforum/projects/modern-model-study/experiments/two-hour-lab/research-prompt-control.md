# Text-conditioning controls for the two-hour Krea lab

Research only, 2026-09-14. No inference, infrastructure operations or shared-code changes performed. Recommendation: **test the negative branch at fixed ComfyUI CFG 1.3 first; consider a CFG1 conditioning blend only after an endpoint preflight.** Neither is established to improve gradual transformation or video quality. Do not combine these controls with the main agent's noise-plateau or Euler-spacing experiments in the same comparison.

## Local evidence and scope

Read [Krea transition controls](../../../../../../docs/research/krea-transition-controls.md), [noise and latent continuity](../../../../../../docs/research/noise-and-latent-continuity.md), the current [package graph](../../../../src/deforum_lab/rendering/graphs.py), [prompt bridges](../prompt-bridges.md), [CFG audition](../cfg-audition.md), [finer stages](../transition-stages/README.md), its frozen configuration and this lab's [round-one plan](README.md).

- `repaint_graph` supplies the warped previous RGB through `VAEEncode` to `SamplerCustom.latent_image`. Positive text is node 4; node 5 zeroes that text conditioning for the negative branch. The sampler uses fresh seeded noise, CFG1, Euler and explicit sigmas. Preserve this recurrent image initialization in every proposed case; RIFE remains finishing only.
- The completed CFG sweep held the zeroed negative fixed. At 1.3, architecture appeared earlier and gained detail, but repaint changes increased. Encoded-empty and subject negatives were not tested. Measured warm jobs were about 8.1s at CFG1.3 versus 4.6s at CFG1 on that older runtime; these are historical timings, not forecasts for today's GPU.
- Finer descriptions produced a broader city sooner, but a largely solid shell at 3.25s became substantially open at 3.5s. Capping later noise softened the last reveal without addressing that earlier jump. Merely retaining the shell longer or adding texture is insufficient.

## Primary-source compatibility findings

Verification targets the project's documented ComfyUI revision `12d5279438bfefc058a269eae805ceab6047777f` and official Krea revision `db3984fbc6e13b34c0064990fc2d95ac64d00058`. Fetched and inspected primary source during this task. This is source compatibility evidence; the active remote runtime and newly proposed graphs were not executed or inspected.

**External guidance works, but Turbo recommends positive-only sampling.** Krea's published Turbo recipe uses eight steps, guidance disabled and shift 1.15. Its reference sampler defaults negative text to an encoded empty string when guidance is enabled. It computes `c + g*(c-u)`; ordinary ComfyUI computes `u + k*(c-u)`, so the convention maps as `k=1+g`. ComfyUI 1.3 corresponds algebraically to Krea 0.3, not a promise of cross-framework pixel parity. At ComfyUI CFG1, the standard sampler skips negative evaluation. [Official Turbo recipe](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/README.md#turbo-oss_turbo), [Krea sampler](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py#L85-L132), [ComfyUI CFG](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py#L592-L627).

**Zeroed, empty and subject conditioning are different inputs.** `ConditioningZeroOut` zeros the embedding and selected auxiliary tensors, retaining other metadata and token length. `CLIPTextEncode(text="")` follows the Krea chat template and encoder; it is not a zero vector. A subject negative is another model prediction, not a literal object-erasing mask. [Core nodes](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L272-L298), [Krea encoder/template](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/text_encoders/krea2.py#L20-L72).

**Unequal positive/negative lengths are supported without embedding averaging.** Krea wraps text with `CONDRegular`; incompatible shapes are not concatenated into a joint batch. Separate predictions can still enter CFG. Different token lengths can affect batching, work and memory. The existing `SamplerCustom` accepts both conditioning inputs directly. [Krea wrapper](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py#L2551-L2571), [condition batching](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/conds.py#L26-L48), [sampler node](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py#L733-L777).

**Blending is structurally possible, with a substantial qualification.** The encoder flattens twelve Qwen3-VL layer outputs to `(B,L,30720)`, which the Krea model unpacks before nonlinear text fusion. `ConditioningAverage` can mix this shape. It weights `conditioning_to` by its strength, truncates/pads `conditioning_from` to the destination length, and retains destination metadata apart from pooled-output mixing. Therefore strength zero need not reproduce the original source conditioning. [Encoder](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/text_encoders/krea2.py#L43-L72), [model text processing](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/ldm/krea2/model.py#L295-L391), [averaging implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L94-L132).

The pinned Krea wrapper does not forward the encoder's attention mask, and the image transformer's text fusion and block calls pass `None` for their masks. **Do not assume padding introduced by averaging will be ignored.** This observation concerns this pinned adapter, not every Krea implementation. Encoding itself still uses attention masking. Also, token positions are not semantic correspondences: even equal-length prompts can mix unrelated words and contextual features. A linear embedding path is not a linear path through architecture. [Wrapper](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py#L2551-L2571), [transformer](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/ldm/krea2/model.py#L339-L370).

## Test 1 — fixed modest CFG, three negative definitions

Question: does replacing the zeroed branch change the route to open architecture usefully, without merely producing a harder flip?

Freeze one noise schedule after round-one review; record its configuration/hash. Keep its original three-interval placement, positive fine-stage prompts, painting timestamps, seeds and motion. Fork all branches from its exact painting at 2s. Do not introduce a new CFG ramp or change positive wording.

| Arm | CFG from 2.25–4s | Negative conditioning |
| --- | --- | --- |
| C | 1.0 | Existing zeroed positive |
| Z | 1.3 | Existing zeroed positive |
| E | 1.3 | `CLIPTextEncode`, exact empty string |
| S | 1.3 | `CLIPTextEncode`, exact text: `A closed intact spiral snail shell.` |

The causal comparison is Z/E/S at the same CFG; C gives context for the cost of enabling guidance. S deliberately targets the intact shell, rather than negating the complete old prompt with its desired brass, lighting and architectural details. It is a subject-negative test, not exact negation of the historical prompt.

Run eight recurrent repaints per arm at 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75 and 4s: **32 jobs maximum** for this initial comparison. Each arm consumes its own previous painting after the shared start. If C already exists in precisely the same runtime/settings, reuse its verified lineage. A one-painting CFG1 empty-negative replay against C is an optional wiring sanity check, not a fifth creative arm. If that differs, resolve runtime/graph differences before interpreting the comparison.

Only if an arm shows useful intermediate openings, continue it and C through 4.5/5s using the identical settling noise and CFG1. This adds four jobs and checks whether the resulting city can settle. Switching guidance off then is shared across the compared continuations; do not attribute that ending to the negative alone. Finish only the informative pair with identical RIFE and 24 fps timing; preserve all paintings.

Exact graph delta, using existing node IDs:

```text
E: 50 = CLIPTextEncode(clip=["2",0], text="")
S: 50 = CLIPTextEncode(clip=["2",0], text="A closed intact spiral snail shell.")
Z: negative remains ["5",0]
E/S: node 9 negative=["50",0]
Z/E/S: node 9 cfg=1.3
All: node 9 positive=["4",0], latent_image=["24",0]
```

Hypotheses: E may yield a more useful low-strength guidance direction than zero conditioning; S may help open the persistent shell sooner. Risks: Turbo is distilled for disabled guidance; extrapolation may amplify contrast, fine-detail churn or abrupt replacement. S can fight the early desired shell/spiral intermediates. Empty versus zero also changes sequence length and template-derived features, so this isolates a practical branch recipe rather than a pure semantic variable. None is a correspondence or geometry constraint.

## Test 2 — conditional CFG1 text blend versus a hard switch

Lower priority. This is a small controlled audition of conditioning arithmetic, not another descriptive-stage sweep. Proceed only if the existing encoder can establish equal tensor shapes and endpoint equivalence without new dependencies or custom nodes. Otherwise park it for this session.

Use this shared prompt skeleton, changing only the bracketed phrase:

`A [rounded brass shell / open brass city] fills a red desert canyon. Curved golden ribs frame the center. Copper towers, engraved bronze panels, small archways and winding stairs fill the scene. Warm amber sunlight reveals deep shaded volumes and fine metallic detail. An intricate surreal painting with a coherent wide cinematic composition.`

Encode the two expanded strings separately with the existing `CLIPLoader(type="krea2")`. These are proposed frozen texts; their token counts have not been measured. Before inference, require one conditioning entry each, matching `(1,L,30720)` shapes/device/dtype, finite tensors, and matching relevant non-pooled metadata. Check the actual token sequence, including shared-suffix positions. If lengths differ, do not silently accept truncation/padding or build padding machinery. Defer the test unless a minimal wording adjustment can be checked and frozen within the remaining time.

Verify `ConditioningAverage` at strengths zero/one reproduces the respective conditioning tensors and model-consumed metadata. On one identical saved warped input, verify both endpoint paintings against direct endpoint encodings in the same runtime. Stop if parity fails. No Krea endpoint checks were performed by this research task.

Then fork two recurrent arms from the same 2s painting, with CFG1, the same frozen noise curve, Euler intervals, seeds and warps:

- **Switch:** old endpoint through 2.75s, new endpoint from 3s onward.
- **Blend:** new-endpoint strengths `0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0` at 2.25–4s respectively.

This is 16 recurrent jobs plus at most four endpoint-check jobs. Both arms use the same new prompt pair, so their comparison isolates switching versus blending; comparison with the original fine-stage film also includes prompt rewriting and must not be attributed solely to blending. The common source image need not be regenerated from the old prompt, since both arms receive exactly the same recurrent initialization.

Exact added core nodes/connections:

```text
50 = CLIPTextEncode(clip=["2",0], text=old_endpoint)
51 = CLIPTextEncode(clip=["2",0], text=new_endpoint)
52 = ConditioningAverage(conditioning_from=["50",0],
                         conditioning_to=["51",0],
                         conditioning_to_strength=alpha)
Blend: node 9 positive=["52",0], cfg=1.0
Switch: node 9 positive=["50",0] or ["51",0], cfg=1.0
node 5 conditioning follows the selected positive; node 9 negative=["5",0]
node 9 latent_image remains ["24",0]
```

Do not substitute `ConditioningCombine`, concatenation, a denoising-timestep range or decoded-image blending: these answer different questions. Alpha changes once per repaint, not inside its three Euler intervals. Arithmetic blending does not add a second diffusion prediction at CFG1, although two endpoint encodings are needed. Hypothesis: a continuous conditioning change may distribute semantic pressure. Risks: nonlinear response can still flip, mixed contextual features may reduce detail/coherence, and a long shell hold can masquerade as smoothness. Guidance extrapolation and this interpolation must remain separate experiments.

## Decision evidence and stop conditions

Inspect every transition painting before interpolation. Require readable structural progress across more than two repaints: seams becoming actual openings, a street developing through them, and an open city arriving by the shared endpoint. Inspect retained ribs, shading, palette, framing and broken/doubled geometry. A different endpoint composition or reduced texture motion alone is not a win. RGB difference from each warped input can locate jumps; it is not a semantic or video-quality score.

For a promising pair, inspect identical RIFE finishing around the largest transition and report whether doubled edges remain. Preserve executed graphs, exact strings, conditioning shapes, CFG, sigmas, seeds, parent/input/output hashes and all attempts. These are single-source, single-seed-path probes; a result warrants a later replication, not a general claim. If neither route distributes meaningful change, report that finding and retain the established recipe. No inversion, training, model replacement, reference adapter or new dependency infrastructure is needed for these proposals.
