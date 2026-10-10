# Pressure Lock

A thirty-second, 136 BPM underground club micro-arrangement. Heavy kick and interlocking F-pedal bass preserve the core qualities Olof approved in Undertow. Original elastic bass articulations and mechanical percussion supply a new rhythmic identity; there is no foreground tune, speech or sampled song recording. The drum foundation uses the retained 909 recordings.

The selected version is `renders/v011/master/render.wav`; `renders/v006/master/render.wav` remains the stable earlier alternative. It is one of the two excerpts selected for Olof to assess; human taste judgment is pending.

## Musical design

The central object is an asymmetric five-sixteenth cell (`hit · · hit ·`). Against a sixteen-sixteenth bar, its position shifts continuously and the composite realigns every five bars. It starts as rounded mechanical percussion against a four-beat kick and interlocking F-pedal bass. One fixed resonator bank and noise excitation gradually change their damping, relative weights and roughness. The low body lengthens as upper ringing is damped; no written melody or descending series of resonator pitches is introduced. At about 11.5 seconds, the ordinary rhythm falls away and the same cell becomes exposed elastic body. Four quick taps and a short gap lead into the return at 14.1 seconds. The object stays in the returned groove as a darker percussion voice while the ordinary bass notes become longer.

The opening establishes the physical groove immediately. A brief earlier pocket exposes the low-end rhythm, secondary ghost/air layers leave room at the main return, and the exit uses a sparse metallic echo. Sixteen active bars plus one effect-tail bar at 136 BPM make exactly thirty seconds.

These are design intentions. Render and stem measurements confirm timing, energy and safe levels; they cannot establish musical taste or perceived impact.

## Revision record

- V001: original metal/air/knock/FM-rubber palette and four compact musical gestures.
- V002: more prominent new percussion and an exposed long bass turnaround; distinct echo ending.
- V003: restored the metal's lower resonator, shortened its decay, reduced its level and filtered its upper edge. A loudness-matched audio-model comparison preferred this rounder percussion to v002.
- V004: alternated a noisier, damped articulation in the metal cell. A comparison with reversed version order preferred v003's body. V004 remains a preserved alternative.
- V005: a larger compositional change. The five-step cell becomes exposed elastic bass while the ordinary groove suspends, then the groove returns with longer bass notes. A randomized comparison of seconds 8–20 identified and preferred this transformation over v003.
- V006: added a matching low-frequency component to the exposed object, then carried its cell into the returned bass groove while removing competing details. It is the preserved stable alternative: it keeps the physical bass intent and gives the transformation a consequence after the return.

- V007–V011: tested one continuous sound family across the role change. V011 keeps fixed resonator frequencies, controls upper ringing and strengthens the noise attack. It is the current candidate. The [continuity study](continuity-study.md) preserves the intermediate experiments, clipped v009 exclusion, comparisons and measurements.

The v005/v006 audio-model comparison claimed the excerpts were identical. They are not: local stem analysis measures approximately 10 dB more bass energy in 30–180 Hz during the exposed passage of v006. Its low-frequency judgment is therefore not accepted as reliable, and no model preference was established between those revisions. Earlier reviews also invented an abrupt ending despite measured decays and reported a lack of sub depth despite strong measured low-frequency content. The measurement establishes that those frequencies exist; perceived physical weight remains a separate, uncertain judgment. We use the clearer, larger structural observations as hypotheses and retain independent waveform checks. No human preference for Pressure Lock has been recorded.

## Modules and assets

`assembly-v011.json` is the current reproducible assembly manifest. The setup, drums, bass, percussion and space modules live in `modules/`; the assembled source and project recipe are preserved in `assemblies/v011/`. The original v001 source and recipe remain preserved separately.

`make_palette.py` creates the original deterministic metal, air, knock and short rubber-bass samples. `make_gesture.py` creates the longer bass articulation. `make_muted.py` preserves the damped articulation explored in v004. `make_damped_morph.py` creates the current shared resonator family; `make_morph.py` and `make_weighted_morph.py` preserve earlier continuity experiments. All generators use local NumPy/SciPy synthesis, with no model calls or downloaded audio. Sample hashes and synthesis descriptions are in `references/palette.json`, `references/gesture.json` and the corresponding morph receipts. The retained 909 kick, clap and hats come from the existing [drum provenance](../practical-dogfood/drum-sources.json).

The `pressure` background synth is intentionally very quiet; it is not counted as a defining audible feature. Per-band analysis shows the new percussion is materially more prominent than the old Undertow texture, and the bass gesture changes midrange energy at the turnaround. Those measurements do not prove that the new timbres are appealing.

## Reproduce

From `apps/music`, with the retained sample folders present:

```sh
uv run --locked python music.py assemble projects/pressure-study/assembly-v011.json \
  --out projects/pressure-study/assemblies/rebuild-v011
uv run --locked python music.py render-project \
  projects/pressure-study/assemblies/rebuild-v011/project.json --revision v011 \
  --out projects/pressure-study/renders/rebuild-v011 --timeout 180
uv run --locked python music.py analyze-project \
  projects/pressure-study/renders/rebuild-v011 \
  --out projects/pressure-study/renders/rebuild-v011/band-analysis --window-cycles 1
```

Fresh paths preserve earlier renders. The v011 master and four stems completed at 48 kHz stereo with aligned frames. The master measures −14.42 LUFS and −1.0 dBTP, with no PCM rails. The end decays below −80 dBFS before thirty seconds. The modular assembler and continuous per-band analysis were exercised on this candidate.

## Final technical and rebuild audit

The preserved v011 master remains the delivery candidate. A separate rebuild in `renders/fresh-v011-audit-02/` regenerated all 29 original sample files from the saved generators and downloaded the four 909 samples from their recorded public sources. All 33 asset hashes matched the retained originals, and the assembled source matched byte for byte. Master and four stems rendered successfully at exactly 1,440,000 frames, 48 kHz stereo, with zero PCM rail contacts. The rebuilt master measures −14.42 LUFS and −0.99 dBTP. The original and rebuilt audio are not bit-identical: the master difference RMS is −46.51 dBFS and the quiet synth/effect material varies. This proves reproducible source/assets and a numerically consistent render, not bitwise deterministic synthesis. See [rebuild evidence](references/fresh-rebuild-v011.json).

[Waveform audit](references/final-audit-v011.json) checks the retained delivery master and each stem. Summing the master to mono loses 0.012 dB overall and 0.006 dB in 30–180 Hz; no substantial low-band cancellation appears in this check. At the eleven inspected arrangement boundaries, the largest adjacent-sample step is −56.5 dBFS. This is a bounded seam check, not proof that no audible click exists anywhere. The final master sample is one 16-bit quantization step below zero in the right channel (−90.3 dBFS), and its last sample at or above −80 dBFS is at 29.602 seconds. No abrupt full-level truncation or technical defect warranted altering v011.

The musical audit preserves the purposeful exposure at 11.47 seconds, the short pre-return gap and the return at 14.12 seconds; it does not fill those spaces with extra material. These timings follow the saved arrangement and waveform evidence. Direct human listening remains the final check for tone, groove and whether the transformation feels compelling.

To repeat the full asset/source/render audit into a new directory:

```sh
uv run --locked python projects/pressure-study/rebuild_audit.py \
  --out projects/pressure-study/renders/fresh-v011-audit-03
uv run --locked python projects/pressure-study/final_audit.py
```

The first two audit sandboxes are preserved: the first stopped during drum retrieval and the second was interrupted after palette generation, then resumed and completed. The scripts never overwrite existing audio.

## Craft references

Dennis DeSantis describes using unequal rhythmic loop lengths to create a moving composite in [Ableton's Making Music](https://makingmusic.ableton.com/asynchronous-or-polyrhythmic-loops). Our five-step metal phrase applies that general technique; its actual pitches, samples and arrangement are original.

Surgeon's [first-person production interview](https://www.musicradar.com/news/surgeon-interview) supports a strict rhythmic foundation with selective variation. Blawan discusses paired oscillators, low-pass gates and resampling in his [first-person interview](https://www.musicradar.com/news/blawan-i-put-the-why-they-hide-their-bodies-track-out-and-was-totally-shocked-by-how-popular-it-was-i-was-kind-of-like-f-ive-made-a-big-mistake-here). These were textual craft references supplied by the collaborating critic, not recordings sampled into this piece or claims of an auditory transcription.

The one-time role transformation also draws on the broad principle in [Unique Events](https://makingmusic.ableton.com/unique-events): a deliberately placed singular gesture can distinguish a loop arrangement. The concrete event here is original. [Subtractive arranging](https://makingmusic.ableton.com/arranging-as-a-subtractive-process) informed removing secondary layers to expose that object.
