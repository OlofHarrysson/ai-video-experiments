# The Night Orchard

An amber fruit glows inside an enormous midnight greenhouse. A journey into its light reveals an orchard suspended among the stars. A short surreal film about small things containing vast possibilities.

Olof delegates direction. The assistant chooses the imagery, operates production, screens results and adapts the next passage to the paintings. The [director's brief](BRIEF.md) and [decisions](DECISIONS.md) own the creative plan.

Current cut: none selected.

## Start the opening audition

From `apps/deforum/`, run `uv run --locked python projects/night-orchard/experiments/film.py plan o1-silver-branch` for an offline configuration check. The second opening is `o2-silver-branch`; both use the same prompt with different recorded seeds. Configuration checks and scoped Ruff checks pass. No inference or delivery has been performed.

After the separate render cap is confirmed and an owned deployment is ready, use the runner's `opening` stage with `--deployment /ABSOLUTE/DEPLOYMENT.json`, then `check`. Inspect the two paintings before writing the first motion plan. The runner's `prepare`, `render --through FRAME`, and `check --through FRAME` stages preserve prefixes and verify recurrent jobs. Finishing uses the established local RIFE workflow after an actual passage is selected.

## Experiments

- [Opening and first passage](experiments/baseline.md): preparation; no inference yet.

[References](references/README.md) · [runs](runs/README.md) · [cuts](cuts/README.md) · [exports](exports/README.md)

Follow the [working convention](../../../../docs/workflow.md).
