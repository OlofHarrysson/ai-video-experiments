# Through the railway doorway

2026-09-16. A revision of **The Open Dream** following Olof's request for movement tailored to the actual artwork and a different world beyond the doorway. The selected film preserves the first nine seconds, keeps the approaching doorway readable, reveals a forest of golden harps, then moves through a gap toward the red train in a green landscape.

[Compare the revision and original](http://localhost:3028/doorway) · [All five attempts](http://localhost:3028/doorway-attempts) · [Frame review](quality-review.md) · [Execution receipt](execution-summary.json)

![Beyond the Threshold — 20 seconds](../../exports/doorway-revision-v001/d5-beyond-the-threshold/faster/rife-moving-tail/preview.mp4)

The assistant selects D5 for the clearer new-world reveal. Human preference is pending. This is an artistic revision with several coupled decisions, not a controlled comparison isolating one parameter.

## Branches and decisions

| Attempt | New paintings | Delivered length | What happened |
| --- | ---: | ---: | --- |
| D1 — Doorway approach | 12 | 13⅓s | Recenter the measured doorway, start pushing earlier, and introduce foliage/harp strings beyond a legible arch. A useful approach, ending before the crossing. |
| D2 — First crossing | 13 | 17⅔s | Push through the measured interior. The forest and red train appear, but the near harp and pale margins crowd the composition. |
| D3 — The music beyond | 11 | 21⅓s | Try a larger lateral reveal/follow. The train changes position during repainting; repeated foreground shapes obscure the ending. Rejected, preserved for diagnosis. |
| D4 — Open glade | 13 | 19⅓s | Rewind to source 22s. Gentler motion and meadow descriptions open a brighter landscape, but a red wall/curtain fills much of the right side. |
| D5 — Beyond the Threshold | 11 | 20s | Rewind to D4 at source 24s. Measure the open gap between the near harp/tree and red wall, then push through it toward the train. The red wall leaves the ending; some translucent string-like remnants and flatter shading remain. |

All 60 new inference jobs remain recorded. The selected film contains 60 paintings: 28 from the preserved opening and 32 new paintings from the selected branches. No earlier film or abandoned branch was overwritten.

## How the movement was composed

1. **Approach:** branch at source frame 324 (13.5 source seconds, 9 delivered seconds), before the clock dominates. Measure the doorway near (1107, 426) in the 1536×1024 painting. Overlap a recentering translation and earlier push with ongoing drift. At this earlier frame the doorway is above/right of center, so the required displacement differs from the later low doorway in Olof's example.
2. **Crossing:** inspect the new painting at source frame 468. Aim through its visible interior near (870, 475); describe the new forest while retaining straight doorway jambs during approach. The first crossing exposes a harp that becomes an obstacle.
3. **Reveal:** the first larger side move fails. Rewind, generate an open glade, then inspect frame 576. Aim at the visible gap near (738, 586), rather than enlarging the foreground harp again. Continue a small drift underneath the bounded pan/push.

[Approach motion preview](../../exports/doorway-revision-v001/review/approach-motion.mp4) · [Approach sheet](../../exports/doorway-revision-v001/review/approach-motion.jpg) · [Final gap preview](../../exports/doorway-revision-v001/review/clearance-motion.jpg)

These previews deform a fixed painting. They help check the route and framing; they do not prove that repainting will retain the same objects or their positions. The geometrical path and the new painted contents must both be inspected. The useful lesson is to aim through an opening and inspect the whole passage, not just solve an endpoint coordinate.

## Controls and timing

Recurrent Krea Turbo, CFG1, three Euler intervals, independent recorded seeds, time-based Lanczos spatial transforms with reflected borders. Every new painting initializes from the encoded warped previous painting plus noise and text. No added reference conditioning, image blending or new model architecture.

Source: 24 fps, one painting per 0.5 seconds. Delivery: 1.5× faster, 24 fps, three paintings per displayed second. RIFE 4.25 scale 1 runs after generation and never enters the feedback loop. The final seven delivery frames use actual spatial warps. D5 has 480 frames over 20 seconds. Noise and scene descriptions are explicit in the immutable [configs](configs); D4 briefly reaches 0.80 to open the scene, and D5 moves from 0.56 through 0.64 to 0.36.

The first 217 delivery PNG frames, through frame 216 / nine seconds, match the previous selected film exactly. This is pixel evidence before video encoding, not an H.264 byte-prefix claim. Later timing and imagery differ. Source timestamps in painting contact sheets must be divided by 1.5 to compare with delivered playback time.

## Review and retention

The new destination is clearer and keeps the red-train motif without repeating the whale/ocean environment. This does not yet establish physically coherent camera travel: close shapes still repaint and obstruct the route, fine details change, and the ending becomes more illustrative. See the bounded painting and interpolation inspection in [quality-review.md](quality-review.md).

All 1,269 entries in the complete remote archive were hash-verified locally. Five deliveries preserve every selected painting and fully decode. The owned Pod, session scratch and 120 owned ComfyUI media files were removed; the existing model cache remains. Posted account debit between snapshots was $0.3617250666, with the starting snapshot taken after provisioning. Reserve **$0.45** for this session, bringing the conservative series total to **$5.85/$10**. At cleanup, the account had no Pods and reported $0.005/hour from retained storage. Media is local and ignored by Git; there is no separate external backup.

## Local commands

Run from `apps/deforum/` with the existing locked uv environment. `run.py` wraps the earlier audited experiment runner; planning scripts write frozen configs and motion previews from their preserved parents. They are not a new shared rendering framework.

```sh
uv run --locked python projects/modern-model-study/experiments/doorway-revision/run.py --help
uv run --locked python projects/modern-model-study/experiments/doorway-revision/contact_sheet.py d5-beyond-the-threshold --frames 324 408 468 528 576 624
uv run --locked python projects/modern-model-study/experiments/doorway-revision/build_reviews.py
```

Generation and delivery scripts intentionally refuse to overwrite existing outputs. Branch under a new case/export when making another revision. Use the shared-terminal `media-review` service for serving the generated review pages.
