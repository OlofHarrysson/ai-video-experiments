# Club phone reference — 2026-10-15

Olof supplied a roughly 17-second phone video from a techno club. He finds our instrument sounds too basic, the melodic ideas flat, and strongly dislikes the current chord/hook part. This broadens the problem beyond the previous rhythm-only comparison. The next proposed test should replace the foreground sound and musical idea in a short sketch, not continue treating rhythm edits as sufficient. No new music or player change was made in this review.

## Preserved inputs

- Original video and SHA-256 provenance: `references/assets/club-phone-20261015/original.mp4` and `provenance.json`.
- Extracted 48 kHz stereo float audio: `references/assets/club-phone-20261015/audio.wav`, 16.949125 seconds. Original file is untouched; decoding/resampling is recorded here. Reference only, not material incorporated into our track.
- Current comparison: `renders/pocket-v001-chords/pocket.wav`.
- Local review evidence: `../../work/club-reference-20261015/` includes inspection, anonymous pair, identical-input control, exact prompts, submitted-audio hashes, model metadata and provider responses. Media and raw provider outputs are ignored by Git.

## Evidence and limits

The comparison used phone seconds 1–16 against our seconds 0–15, a one-second separator, and attenuation to −17.52 LUFS. The retained answer key maps A to the phone recording and B to Undercurrent. No compression or equalization was added. The raw phone decode peaks at +0.46 dBFS; matched comparison attenuation avoids overload. The duplicate control received constant −8 dB attenuation to avoid those decoded peaks, with its halves verified sample-identical before submission.

The current OpenRouter catalog identifies `google/gemini-4-argon` as Google's flagship with audio input; both requests used high reasoning through OpenRouter/Google, completed with `finish_reason: stop`, and reported $0.041898 combined. The review adapter's default model was not changed. The control correctly identified identical copies. This is narrow route evidence, not validation of taste or exact musical descriptions.

The model described the club reference as a pulsing, swelling pitched texture that builds tension and recedes, and our excerpt as short syncopated stabs with a repetitive pitched idea. It could not reliably separate the club bass/percussion from room and crowd sound. Claimed exact pitch motion and production mechanisms remain unverified. Its assertion that our timbre is completely static is too strong: the source changes filtering and velocity. Its perception of limited development is a hypothesis, not proof those controls do nothing.

Source inspection gives firmer guidance: our chord is a fixed rendered harmonic sample, with a 0.19-second exponential amplitude decay and rapid darkening over about 0.075 seconds. Subsequent filtering cannot restore upper-frequency energy already removed from that sample. The first 15 seconds repeat one chord voicing and a two-bar rhythm. The full 30 seconds do include a later voicing change, break and ending, so the excerpt does not establish an absence of arrangement.

## Proposed next comparison

Keep the established drum/bass foundation initially so the foreground change is legible. Replace the rejected chord motif with two 10–15-second alternatives: a connected, evolving pitched texture and a sparse, more distinctive percussive idea. Design their source envelopes and harmonic movement deliberately; do not merely add more notes or reverb to the existing sample. Compare in the shared player at similar levels and let Olof choose before extending. Revisit the drum/bass timbres afterward; retaining them for this comparison does not imply their sound quality is approved.

Codex did not hear browser playback directly. The conclusions above distinguish user taste, actual audio-model observations, source inspection and numerical measurements. Phone acoustics and the PA are confounds when judging studio sound quality or stereo width.
