# Brain Entity style study

Original six-second transformation inspired by the graphic qualities of [Brain Entity](../reference-studies/references/brain-entity.md): bold black ink, teal/ivory/orange forms and a mechanical opening becoming organic.

Current state: six stills, the original two style videos, six parameter comparisons, and the [continuity study](experiments/continuity.md) are preserved. [Style baseline v002](exports/v002/preview.mp4), with [v001](exports/v001/preview.mp4) retained for comparison, established the direction for the later comparisons. Olof says v002 is much closer to his intention, but still not great.

The [parameter study](experiments/parameters.md) adds six controlled comparisons. Holding the opening prompt constant (P06) preserves midpoint detail, but Olof finds its motion too discontinuous. P01/P03 and likely P04 are the stronger motion references. The [continuity study](experiments/continuity.md) adds noise comparisons, Flow Stabilize and RIFE finishing. **P3 + RIFE is now the tentative favorite**; C01/C03 were boring, and the other outputs were pretty good. Similar variants were difficult to distinguish. The [review harness practice](experiments/review-harness.md) introduces assistant screening, every-frame windows and matched comparisons before another generation round.

- [First experiment and findings](experiments/style.md)
- [Controlled parameter comparisons](experiments/parameters.md)
- [Temporal continuity results](experiments/continuity.md)
- [RIFE interpolation results](experiments/rife-results.md)
- [Review harness practice and current baseline](experiments/review-harness.md)
- [Parameter runner](experiments/parameters.py)
- [Guide generator](experiments/make_guide.py)
- [Render recipe](experiments/render.py)

All reference guides, source images, cloud attempts and exported videos remain local and ignored by Git. The guide is original geometry; no reference video frames are used as generation inputs.
