# Frozen RunPod session source

These files record the 2026-09-27 experiment, not a general deployment service. `session-worker.py` includes that session's absolute expiry; change it for a newly authorized run. It expects `assets/`, `requests/*.json`, and a `qwen21_fun/` module beside it. Request recipes are recorded in `../run-index.json`; the exact submitted JSON, source module, environment and outputs are preserved locally in `apps/comfyui/work/spatial-control-lab/remote-final.tar.gz`.

`load_pipeline.py` was adapted from [the public demo](https://huggingface.co/spaces/hugging-apps/qwen-image-2-1-controlnet-union-demo/tree/93f834f7b3bf4c8f5bda498deabe0255e9fe9809): UI/ZeroGPU decorators removed, model revisions pinned. Download `qwen21_fun/` from that same revision, including `LICENSE-VideoX-Fun`. No changes were made to those vendored model modules. Full BF16 weights loaded with zero missing/unexpected keys.

Environment: official `runpod/comfyui:cuda12.8` image pinned to `sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`, Python virtual environment inheriting its torch 2.10.0+cu128; diffusers 0.40.0, transformers 5.17.0, accelerate 1.15.0, huggingface-hub 1.33.0. A100 SXM4 80 GB. Models: base revision `790c92633540aa0cb11d9abf19eb46d861714758`, control revision `8a4702014d4dabb5f896fcba917e2ee0a961465f`.

All 24 outputs were downloaded and SHA256-verified before deleting the session's Pod. Existing shared storage was untouched. Follow the repository's Pod runbook before provisioning again.
