# Swap test

Status: v002 approved by Olof on playback: "Looks great." (2026-09-27). Shareable loop: [renders/swap-test-v002-loop3.mp4](../renders/swap-test-v002-loop3.mp4).

## Question

Do generated variations of one composition, swapped twelve times per second under a slow pull-back, read as time passing?

## Comparison

- **Changes with every image:** hair, clothes, light and palette, from the 23 variations in [swap-test.json](swap-test.json).
- **Fixed:** one original character, chosen by Olof on 2026-09-27; her bowed head, closed eyes and outstretched hands; the framing; the table, window, curtains and plant; the watercolor style. Every variation edits the same chosen base painting, never a previous variation, so drift cannot accumulate.
- **Timing:** 24 images held for two frames each, 2 seconds at 24 fps. [assemble.py](../scripts/assemble.py) pulls back from 62% to 100% of the frame with an ease-in-out, moving on every frame. No interpolation.
- **Reference:** film images 1–24, the close-up phase from 3:57.6 to 3:59.6, where the film pulls back from face to shoulders.

## Model and cost boundary

- Seedream 4.5 through fal, chosen by Olof on 2026-09-27 as three times cheaper than Nano Banana 2, leaving room for several iterations: text-to-image for four base candidates, then edits of the chosen one.
- Size 4096×1920, the widest Seedream allows: each side must be 1920–4096 px. The assembler crops the 2.4:1 frame from it.
- $0.04 per image for [generation](https://fal.ai/models/fal-ai/bytedance/seedream/v4.5/text-to-image) and [editing](https://fal.ai/models/fal-ai/bytedance/seedream/v4.5/edit), checked 2026-09-27. Plan: 4 base candidates, 23 variations and up to 8 retries, about 35 images or $1.40. [generate.py](../scripts/generate.py) refuses any batch that would pass the run's $3.00 cap in the config.
- Alternatives considered: Nano Banana 2 edit at $0.12 per 2K image, the model to compare if Seedream drifts (its $0.06 half-resolution option is too small for the crop); FLUX.2 Klein on the existing RunPod volume, which avoids a new account but needs a 16 GB download, a new edit graph and weaker editing; Vertex AI through the logged-in Google Cloud account, which would bill an unrelated project.

## Procedure

1. `uv run --script scripts/generate.py base experiments/swap-test.json`; choose the candidate with the clearest pose and composition.
2. `uv run --script scripts/generate.py vary experiments/swap-test.json RUN_DIR base-N`.
3. Screen a contact sheet. Regenerate, with `--only`, any variation whose head, pose, framing or closed eyes changed; rejects stay in the run.
4. Assemble the chosen base and variations with `scripts/assemble.py`, anchored on her face.
5. Show Olof the clip beside the reference's first two seconds.

## Runs and findings

### Run `swap-test-20260927-144926`

Local and ignored: `runs/swap-test-20260927-144926/`. `records.jsonl` holds every call's prompt, seed, output hash and cost; `swap-test-v002-order.txt` lists the assembled images.

- **Cost and time:** 28 calls and 31 images for $1.24 of the $3.00 cap. Four base candidates took 85 seconds; the 23 variations about four minutes with four parallel calls. Seedream returned 4096×1920 JPEGs.
- **Base:** base-2, the largest and most symmetrical figure. Rejected: base-3 holds hands and also presses a second pair of hands together; base-1 raises her arms like a cheer; base-4 is sound but smaller in frame.
- **Composition lock:** measured by phase correlation of edges in the table, hands and jug region, against base-2, then checked by 50/50 blends. 21 of 23 first-pass variations stayed within 8 px at 4096 wide. Variations 21 and 23 moved the girl and table down while the background stayed, by up to 180 px, which shows as doubled arms in a blend. A plain retry fixed 23. Variation 21 drifted with the original bucket hat and again with sunglasses; it held once the striped sailor top and "beach-summer" light became a coral linen shirt and "a bright summer afternoon". Assistant hypothesis, not tested: the beach cue, which put an ocean in the window, invited the model to re-stage the scene. The config now holds the working prompt; the drifted attempts remain in the run.
- **Delivered:** `swap-test-v002.mp4`: base-2 and the 23 screened variations, 48 frames, 2.00 seconds, every image within 8 px of the base. `swap-test-v002-vs-film-loop3.mp4` stacks it above the film's first two seconds, looped three times; both change image on the same frames. `swap-test-v001.mp4` is the first assembly, which still contains the drifted 21 and 23.
- **Assistant screening:** the swaps read as one held moment on changing days. Pose, hands and set stay put while hair, clothes, window and palette change on every image. Unlike the film, her age, the people at the table and the table dressing never change, so it may read as changing outfits rather than passing years. Some shirts carry invented lettering, visible only on single frames.

### Three-speed cut

Olof's request after approving v002, 2026-09-27: the same 24 paintings played three times, slowing down each pass, starting at a quarter second because two frames felt too quick. `swap-test-v002-three-speeds.mp4` (local, 42 seconds) holds each painting for 6, 12 and then 24 frames, 0.25, 0.5 and 1 second at 24 fps, and restarts the pull-back in each pass. Every hold was verified on the decoded file. `swap-test-v002-three-speeds-share.mp4` is the same cut at CRF 23, 14.2 MB, for messaging apps.

Olof then found all three passes a little slow and asked for 4, 8 and 16 seconds. `swap-test-v002-speeds-4-8-16.mp4` (local, 28 seconds) holds each painting for 4, 8 and then 16 frames, a sixth, a third and two thirds of a second; timing verified on the decoded file. Its share copy is 11.6 MB.
