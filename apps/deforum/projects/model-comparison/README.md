# Lantern marsh model comparison

Compare one preserved still from each hosted image model using the lantern-marsh prompt. Static scene composition and painting detail are separate questions from feedback animation compatibility.

- [Experiment](experiments/hosted-stills.md)
- [Runnable recipe](experiments/hosted_stills.py)
- [Session findings](../../../../docs/research/model-comparison-session.md)

Run from `apps/deforum/` with the existing `uv` environment. No extra packages are required. The recipe only invokes named public image APIs; it cannot create or modify infrastructure.

```bash
uv run python projects/model-comparison/experiments/hosted_stills.py plan
uv run --env-file .env python projects/model-comparison/experiments/hosted_stills.py run flux-dev
uv run --env-file .env python projects/model-comparison/experiments/hosted_stills.py run seedream-4
```

Optional fal models use `run flux-2-pro` and `run seedream-5-lite` after `FAL_KEY` (or `FAL_API_KEY`) is available in the environment. `uv run --env-file .env` loads the ignored app credentials without the recipe reading other credential files.

Each run has immutable request/receipt files, source URLs, API responses, original downloads and SHA-256 hashes. `collect RUN_NAME` recovers an existing submitted job without buying another generation. Ambiguous submission errors must be reconciled with provider history before any new run. Each submit reserves $1 against a project-local $5 RunPod/$2 fal cap, including failures and ambiguous submissions. This is a conservative client guard, not a provider billing limit. Prices must be rechecked if reusing this dated recipe.
