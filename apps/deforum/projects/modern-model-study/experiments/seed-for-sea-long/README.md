# A Seed for the Sea — long journey

Continuation of the [24-second short](../seed-for-sea/README.md), requested after Olof said he quite likes it and wants roughly 1.5–3 minutes. The completed cut is **120 seconds at 24 fps**, retaining all 72 original paintings and adding 288 new ones. [Watch and step through the film](http://localhost:3028/seed-for-sea-long), [open the local video](../../exports/seed-for-sea-long-v001/film-v001/preview.mp4), or inspect the [screening notes](quality-review.md). The original short remains available.

The pearl passes its light between worlds. The approved opening finds water in a dry shell and grows a floating garden. Its reflection leads below the surface into a carved city. A hanging pearl becomes a glass bell, then a jellyfish; the architecture unravels into current. Jellyfish become lanterns whose red boat baskets rise into the sky. The lanterns pour water onto the dunes, the shell returns as a fountain, and roots and flowers spread into a garden. Tiny traveler-like figures emerge in the ending without controlled character identity. [Brief](BRIEF.md), [observed decisions](DECISIONS.md).

## Production

The opening and every repaint use the same Krea Turbo model. Each new painting consumes the spatially warped previous painting. CFG 1; three Euler intervals; independent recorded seeds; staged text descriptions and scene-specific noise ramps. Motion includes directed approaches, lateral travel, pullbacks, rolls, plane turns and local waves/curls. The previous painting remains the input when the scene changes.

Source 24 fps/cadence 12; presentation 24 fps at 1.5× source speed. Every painting is retained, producing three paintings per displayed second. RIFE 4.25 scale 1 fills the intervals after generation; it does not enter the feedback loop. The final seven frames continue spatial warping.

Each passage begins at an existing painting and preserves its prefix. Its new motion field fits the incoming translation, scale and roll before continuing; the recorded residual describes the approximation when the parent field contains local deformation. Previewing that path on the actual artwork precedes paid generation. A halfway inspection can stop or redirect the continuation.

The original 72 paintings are preserved. The original film remains available separately. The long edit removes each nonfinal excerpt's shared last painting and seven temporary warp frames, then takes that painting from the next excerpt exactly once. Frame hashes verify each boundary. This avoids a duplicate hold and retains every unique painting.

## Reproduce and inspect

Use `uv run --locked` from `apps/deforum`. `run.py prepare/render/check` reuses the established experiment runner. `review.py` extracts bounded painting sheets or renders a motion-only preview; `direction.py` creates a new immutable continuation configuration. `finish.py CASE` finishes only its new passage. `assemble.py EDIT OUTPUT` joins verified passages and validates frame hashes, painting cadence, encoded timing and decode success.

Media and raw execution histories live under `projects/modern-model-study/exports/seed-for-sea-long-v001`. Configuration, edit decisions and delivery receipts are tracked here. Every unique generation and its remote records must be retrieved and hash-verified before deleting the session's GPU.

The completed session archived and verified 5,905 files locally, including all 288 new paintings and their execution records. The final video passes full decode, timing and painting-retention checks. The owned Pod was deleted and its absence verified; the shared model volume remains. Estimated compute and disk cost was **$1.09**, within the additional $10 allowance. Concurrent account spending is excluded from this estimate. See the [execution summary](execution-summary.json) for hashes, validation and resource receipts.
