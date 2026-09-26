# Swap test

Status: ready to run; generation waits for a fal API key in this project's `.env`.

## Question

Do generated variations of one composition, swapped twelve times per second under a slow pull-back, read as time passing?

## Comparison

- **Changes with every image:** hair, clothes, light and palette, from the 23 variations in [swap-test.json](swap-test.json).
- **Fixed:** one original character, chosen by Olof on 2026-09-27; her bowed head, closed eyes and outstretched hands; the framing; the table, window, curtains and plant; the watercolor style. Every variation edits the same chosen base painting, never a previous variation, so drift cannot accumulate.
- **Timing:** 24 images held for two frames each, 2 seconds at 24 fps. [assemble.py](../scripts/assemble.py) pulls back from 62% to 100% of the frame with an ease-in-out, moving on every frame. No interpolation.
- **Reference:** film images 1–24, the close-up phase from 3:57.6 to 3:59.6, where the film pulls back from face to shoulders.

## Model and cost boundary

- Nano Banana 2 (Gemini 3.1 Flash Image) through fal: text-to-image for four base candidates, then edits of the chosen one, at 21:9 and 2K. Verify the delivered size before assembly; the pull-back crops a 2.4:1 window.
- $0.12 per image at 2K ([fal pricing](https://fal.ai/models/fal-ai/nano-banana-2/edit), checked 2026-09-27). Plan: 4 base candidates, 23 variations and up to 8 retries, about 35 images or $4.20. [generate.py](../scripts/generate.py) refuses any batch that would pass the $6.00 cap in the config.
- Alternatives considered: Seedream 4.5 edit at $0.04 and up to 4 MP, the cheaper model to compare if Nano Banana drifts; FLUX.2 Klein on the existing RunPod volume, which avoids a new account but needs a 16 GB download, a new edit graph and weaker editing; Vertex AI through the logged-in Google Cloud account, which would bill an unrelated project.

## Procedure

1. `uv run --script scripts/generate.py base experiments/swap-test.json`; choose the candidate with the clearest pose and composition.
2. `uv run --script scripts/generate.py vary experiments/swap-test.json RUN_DIR base-N`.
3. Screen a contact sheet. Regenerate, with `--only`, any variation whose head, pose, framing or closed eyes changed; rejects stay in the run.
4. Assemble the chosen base and variations with `scripts/assemble.py`, anchored on her face.
5. Show Olof the clip beside the reference's first two seconds.

## Runs and findings

No runs yet.
