# Exports

`v001/` preserves the two opening auditions, recurrent continuations and ending revision. Each case owns immutable `config.json`, `anchors/`, source lineage and generation checks; `v001/runs/` holds each ComfyUI graph, history and original PNG.

Use this project's `experiments/finish.py` for delivery. It maps source paintings at frames 0, 12, 24… to delivery frames 0, 8, 16… at 24 fps. Its `pair`, `full`, `tail` and `check` stages operate in `faster/`, or `through-NNNN/` for an explicit checkpoint. Inspect the first pair before full interpolation. `rife-moving-tail/preview.mp4` is the final delivery, with adjacent frame-role and verification records.

`motion-previews/` contains camera-only studies. These warp a single actual painting and cannot predict newly generated scenery. `media-review-v001/` contains the human review page. All generated images and video remain local and are ignored by Git.

See the [working convention](../../../../../docs/workflow.md).
