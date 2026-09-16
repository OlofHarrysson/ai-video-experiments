# The Night Orchard

One amber pear hangs from a silver branch in a midnight greenhouse. Its branching veins become trees, and the scene opens into an orchard of floating islands among the stars.

**Selected cut: 16 seconds, silent, 1536 × 1024, 24 fps.** [Play in the local reviewer](http://localhost:3028/night-orchard) · [MP4](exports/v001/p5-the-final-glide/through-0564/rife-moving-tail/preview.mp4) · [cut record](cuts/v001.md).

Olof delegated direction after our [retrospective](../../../../docs/lessons-learned.md). The assistant selected the opening, planned each move from actual paintings, screened checkpoints and revised the ending. The [brief](BRIEF.md) records the intended film; [decisions](DECISIONS.md) and the [production report](experiments/baseline.md) explain what the material actually became. Human feedback is pending.

The world transformation reads more clearly than a literal journey into the fruit. Small leaves and architecture redraw, and later paintings flatten. The selected edit ends before the weakest extended ending. Both openings, all continuation paintings, the rejected pullback and the complete 20-second source sequence remain preserved locally.

## Production and verification

Krea generated the opening and recurrent paintings. The selected film retains 48 original paintings; RIFE supplies the intervals and the final seven frames continue the camera warp. The complete session produced 76 unique paintings across both openings and two ending attempts. Generation provenance, preserved prefixes, delivery timing, all frame hashes and full video decode passed. The reviewer played through to its final frame.

The [execution summary](experiments/execution-summary.json) records exact output hashes, checks, review limits and estimated cost. The owned Pod and its session copies were removed after verifying local preservation; the retained model volume remains. Olof's [standing spending authorization](../../../../docs/runpod.md#spending-authorization) replaces the earlier session caps.

## Project tools

From `apps/deforum/`, `experiments/film.py` provides `plan`, `opening`, `prepare`, `render` and `check`, with an explicit case name. Inference requires an owned deployment receipt. `experiments/preview.py CASE --until SOURCE_SECONDS` previews a move on its source painting. `experiments/finish.py CASE pair|full|tail|check` delivers it; `--through-frame 564` selects this cut. Existing outputs are immutable. Inspect the first pair before full interpolation.

[Configurations](experiments/configs) · [exports and frame meaning](exports/README.md) · [working convention](../../../../docs/workflow.md)
