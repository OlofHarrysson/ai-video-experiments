# One object changing material

This study preserves v006 and tests whether its mechanical cell can change material continuously, instead of switching between separately synthesized metal and rubber sounds. All versions retain the physical kick/sub foundation, the five-sixteenth cell, and the original 30-second structure. The new family replaces the old chain, transform and returned cell-bass layers; it does not add another simultaneous foreground part.

The same deterministic excitation and resonator phases produce thirteen original articulations. Each event has an explicit sample index in the source. The event map in `references/morph-arrangement-v007.json` applies to v007–v011. The cell starts metallic, changes during cycles 5–8, then returns as a darker object with a longer body. The returned groove has fewer simultaneous foreground parts than v006.

| Revision | Material change | Result |
| --- | --- | --- |
| v007 | Resonator frequencies converge from inharmonic metal toward low F harmonics; damping lengthens | Audio comparison identified a prominent evolving foreground, but described a melodic arpeggio. That pitch-movement risk is material given Olof's direction. |
| v008 | Same material, stronger foreground level | Preserved level experiment. No independent listening preference established. |
| v009 | Fixed resonator frequencies; changing weights, damping and roughness | Comparison described greater resonance but poorer rhythmic definition. Raw master contains 10 PCM rail samples and is excluded from delivery. |
| v010 | Same fixed bank at lower foreground level | Clean raw render. More presence than v006, but no separate listening preference established. |
| v011 | Low resonances lengthen while upper resonances become more damped; stronger noise attack | Clean raw render. The randomized changed-passage comparison preferred its transformation and return to v006, without describing a melody or continuous wash. |

`make_morph.py`, `make_weighted_morph.py` and `make_damped_morph.py` preserve each sound recipe. Their corresponding JSON receipts record seeds, parameters, sample hashes and generator hashes. All audio is original local synthesis. No new recording samples, TTS or generation provider was used.

## Measurements and interpretation

In the returned groove, 14.2–20 seconds, v011 measures −15.20 / −23.38 / −34.96 dBFS for low (30–180 Hz), body (180–1200 Hz), and presence (1200–6000 Hz). V006 measures −15.41 / −24.59 / −38.41 under the same mono, fourth-order Butterworth analysis. The presence change is about +3.5 dB; the low foundation stays within 0.3 dB. See `references/morph-band-comparison.json` for all intermediate values. Independent band levels are not additive energy shares or proof of perceived quality.

V011 is exactly 30 seconds, 48 kHz stereo, −14.42 LUFS, −1.0 dBTP and has no PCM rail samples. Its last audible decay falls below the inspection threshold before the file ends. The selected audio remains a candidate for human listening, not a claim of professional quality.

The first comparison was seconds 8–20, randomized and loudness-matched, with the answer key withheld from the review prompt. The fuller check uses seconds 0–29 from each version with a two-second separator, fitting the listening tool's 60-second limit; the omitted final second contains only the end of the quiet tail. Provider observations are fallible: previous checks missed a measurable low-band change, and several reviews exaggerated timbres or inferred production methods. We use concrete structural observations alongside independent render checks.

The fuller comparison also preferred v011, but wrongly attributed the difference to delayed hi-hat/shaker entrances. The drum modules are unchanged. Its preference is retained as a weak screening observation, while that arrangement explanation is rejected. The v011 selection reflects the intended shared-material design, stronger measurable articulation and clean render; no human preference is established.
