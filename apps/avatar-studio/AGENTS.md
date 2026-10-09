# Character studio

Paused at Olof's request on 9 October 2026. Preserve the completed experiments; do not resume generation without a new request. This app belongs to the parent AI Video Experiments repository.

Read `README.md` for the workflow, architecture, budget and limitations. Research lives in `docs/competitors.md` and `docs/open-models.md`; speech provenance is `docs/generation.json`; style-transfer inputs, request IDs and spending are in `docs/experiments/restyle.json`. Results are in `docs/experiments/restyle.md`.

The completed motion-transfer experiment is in `docs/experiments/motion.md` and `docs/experiments/motion.json`, with the comparison at `/motion.html`. Source and output are already saved; inspect that state before submitting or regenerating anything.

- The current experiment is rough 3D animation → AI-styled video. Olof directs the character conversationally; the agent operates the production tools. Use placeholders for script and voice. Prioritize visual and performance validation, use an existing rig for future animation work, and do not expand the character control panel.
- Preserve the $50 cumulative budget. Recheck model rates before any paid call and record request IDs and estimated charges. No recurring subscription is authorized by this prototype.
- Use Terminal Manager for service lifecycle. Run `npm run verify` after changes and inspect the affected browser flow.
- Preserve the boundary between stock voice, local voice and a future Olof clone. Do not describe audio-energy mouth animation as phoneme-accurate lip-sync.
- Keep personal reference material and rendered exports under ignored `.private/`. No public deployment is authorized.
- Work on the parent repository's existing branch and checkpoint reviewed changes. Follow its publishing and media-storage conventions.
