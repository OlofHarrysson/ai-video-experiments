# Cuts

No cut selected yet. Save the first as `v001.md`; revisions get a new version. Point the project README's “current cut” to the selected version.

Each cut has a short intent and a table:

| Order | Source relative to project | Source FPS | In frame, inclusive | Out frame, exclusive | Intent |
| --- | --- | --- | --- | --- | --- |

For example, a five-second range in an 8 FPS PNG sequence is `[0,40)`. In its 24 FPS preview the same duration is `[0,120)`. Name which source is being cut. Keep rejected sources and old cut versions.

`experiment.py assemble` creates the cut note and export from an explicit JSON range list. It copies source frames unchanged, records their hashes, and refuses to overwrite an existing cut version. See the [serverless runbook](../../../serverless/README.md) and [working convention](../../../../../docs/workflow.md).
