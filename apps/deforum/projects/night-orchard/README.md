# The Night Orchard

An amber pear in a midnight greenhouse opens into an orchard of floating islands. Following its roots leads through a dark sea and a glass garden, then into hanging seeds and a rooted silver tree at dawn.

**Selected cut: 1 minute 56 seconds, silent, 1536 × 1024, 24 fps.** [Play in the local reviewer](http://localhost:3028/night-orchard) · [MP4](exports/v002/x06-the-first-light/through-4164/rife-moving-tail/preview.mp4) · [cut record](cuts/v002.md). The original [16-second cut](cuts/v001.md) remains available in the reviewer.

Olof delegated direction after our [retrospective](../../../../docs/lessons-learned.md), called the first film “pretty good” and requested 1.5–3 minutes. The assistant preserved that opening and directed six additional movements from actual paintings, using independent composition and transition reviews. The [brief](BRIEF.md), [decisions](DECISIONS.md) and [long-cut report](experiments/long-cut.md) separate intended scenes from observed results. Human feedback on the long cut is pending.

The film connects its worlds through amber light and silver branching forms. It supports poetic transformation rather than literal object transport. Fine details redraw; the water-to-glasshouse transition has a brief translucent overlap, and the glass garden becomes less distinctly underwater. The new middle alternates intricate architecture with quieter botanical compositions. All unique generations and both versions remain preserved locally.

## Production and verification

Krea generated the opening and recurrent paintings. The long film retains 348 paintings: 48 from the first cut plus 300 new paintings. The complete generated sequence has 360 paintings; its last four seconds remain preserved because their shading and amber light weaken. RIFE fills the intervals; the final seven frames continue the camera warp. Source lineage, anchor retention, delivery timing, frame hashes and full video decode passed. The [execution summary](experiments/execution-summary-v002.json) records exact output hashes, review limits, preservation and compute cost.

## Project tools

From `apps/deforum/`, `experiments/film.py` provides `plan`, `opening`, `prepare`, `render` and `check`, with an explicit case name. Inference requires an owned deployment receipt. Config `export_version` selects v001 or v002. `experiments/preview.py CASE --until SOURCE_SECONDS` previews a move on its source painting. `experiments/finish.py CASE pair|full|tail|check --version v002` delivers the long cut; `--through-frame 4164` selects this cut. Existing outputs are immutable. Inspect the first pair before full interpolation.

[Configurations](experiments/configs) · [exports and frame meaning](exports/README.md) · [first production report](experiments/baseline.md) · [working convention](../../../../docs/workflow.md)
