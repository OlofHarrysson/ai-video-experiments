# First audio comparison findings

2026-10-10. These observations come from actual audio submitted to Gemini 3.1 Pro Preview, with high reasoning through OpenRouter. They are model hypotheses, not an independent human listening verdict. Full tracks were acquired, but this first pass reviewed only the recorded 28-second windows.

## What the reference comparison changes

In both pairwise comparisons, the model distinguished our instrumental plucked foreground from a sustained, vocal-led reference. It described the references as denser and more spatially diffuse, with foreground performance supported by sustained layers. It described our track as sparse, centered and dominated by brief mallet-like notes. Swapping the reference/candidate order between the two comparisons did not reverse these broad descriptions.

The direct implication is to test **contrast between transient and sustained sounds, and a more expressive foreground**. Another brighter pluck preset alone is unlikely to address the difference identified here. This is not evidence that Olof requires a vocalist: an original sustained instrument, resampled texture or vocal performance would be different candidate solutions requiring listening comparison.

The references themselves can include bright, percussive leads. The model describes that trait in Airglow and Easy, where a vocal or sustained foundation changes its musical role. We should not treat all short synth sounds as inherently game-like based on one rejected composition.

## Track-specific hypotheses

| Reference | Model description of this excerpt | Useful experiment |
| --- | --- | --- |
| Cycles | Breathy lead performance and vocal fragments, sustained pads and a pulsing low end; strong contrast with our isolated plucks. | Give one expressive foreground phrase enough duration and support to carry a section. |
| Castles | Processed, sustained vocal against a dense pulse and layered synths. | Compare a fuller sustained bed against the same rhythmic motif at matched level. |
| Airglow | Airy vocal tails against a rapid plucked sequence, followed by rhythmically pulsing layers. | Let a short sequence articulate a longer sound instead of making every part short. |
| Array | Rhythmic vocal fragments and swelling chords, then a denser arrival. | Make one fragment evolve from rhythmic texture into foreground identity. |
| Easy | Short pitched fragments and a busy lead give way to sustained vocal phrasing. | Change the foreground's articulation across a phrase boundary while retaining the groove. |

Exact claims about sidechain compression, pitch correction, reverb algorithms or waveform types are unverified. Similar audible behavior can be produced by different processes. Model-provided timestamps were not accepted as measured arrangement markers.

## Independent evidence and limits

All comparison excerpts measure −18.07 LUFS except our excerpt at −18.08 after matching; none clips. The measured left/right correlations are Cycles .664, Castles .886, Airglow .633, Array .808, Easy .815 and our excerpt .976. This supports a difference in stereo similarity over these windows, not a judgment that wider is better or proof of perceived depth.

The unannounced identical-audio control passed: the model explicitly said both copies were identical. The waveforms were checked sample-for-sample. This reduces concern about invented contrasts in this one easy condition; it does not validate subtle mix advice, aesthetic judgment or the exact processing claims above.

Six reviews completed with `finish_reason: stop`, reporting **$0.141966** total. [Evidence](evidence.json) records hashes, costs, receipts and validation. No paid retry or fallback model was used.

## Next production test

Use one of these preserved references beside a 15–30-second original sketch. Test an expressive sustained foreground plus complementary short rhythmic material, using the existing render, stem and loudness-matching workflow. Keep the work small enough to change its sound before arranging a full track. Olof's detailed taste direction remains open; this study does not settle vocals, genre or a specific favorite song.
