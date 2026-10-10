# Practical music foundations

A working reference for composing and revising; these principles guide experiments and do not substitute for listening.

## Rhythm and groove

In four-beat bars, Strudel `setcpm(BPM/4)` makes one cycle a bar. A beat lasts `60/BPM` seconds, an eighth note `30/BPM`, a bar `240/BPM`. At 120 BPM, an eight-bar phrase lasts 16 seconds. More events inside the same cycle produce subdivisions, not a longer bar.

Start with a clear pulse and a small rhythmic relationship: kick placement, a snare/clap backbeat, then hats. Syncopation accents weak beats or offbeats; a rest can create anticipation. Swing delays part of a subdivision, while velocity variation changes emphasis. Neither requires every layer to be displaced equally. Listen for how bass attacks fit between or reinforce kick attacks.

Practice: retain the same kick/snare and change only the hat rhythm; then try changing only the bass onset pattern. Preserve versions to hear which change matters.

## Pitch, harmony and voicing

A scale is a pitch collection, not a guarantee of a good melody. A minor triad contains root, minor third and fifth: C–E♭–G. A major triad uses a major third: C–E–G. Octave/register and chord voicing strongly affect texture even when the chord name is unchanged.

Keep the low register sparse; close chord clusters can become hard to distinguish there. Put bass roots below the main chord voices. Move nearby chord tones by small steps to make transitions smoother, or deliberately jump registers for contrast. Inversions put another chord tone in the bass; voicing describes the wider distribution and doubling of tones.

In Strudel, `note("[c3,eb3,g3]")` is simultaneous; `note("c3 eb3 g3")` is sequential. `n("0 2 4").scale("C4:minor")` uses scale degrees, not MIDI note numbers.

## Motif and arrangement

Give the listener something recognizable: a short rhythm, melodic shape or sound gesture. Repeat it enough to establish identity, then change one property—ending, rhythm, register, timbre or accompaniment. A call and response can be a motif followed by a different answering phrase or silence.

Use 4/8/16-bar phrases as a starting scaffold, not a compulsory formula. Plan an opening, arrival, contrast and return. A return can feel stronger because drums or bass were removed beforehand; adding more layers is only one way to increase energy. Mark transitions in the source and listen across their boundaries rather than reviewing only steady loops. Olof became bored with earlier repeating beats: prioritize meaningful development over merely changing BPM.

## Sound and space

ADSR shapes a sound's time envelope: attack, decay, sustain level and release. Short envelopes make percussion/plucks; slower attacks and releases create pads and overlap. A low-pass filter removes higher frequencies; resonance emphasizes a region near the cutoff. Filter movement changes brightness but does not replace melodic or structural development.

Kick and bass can compete in low frequencies. First adjust note length, timing, octave and level; reach for EQ when those choices cannot solve the role conflict. Reverb/delay add space and tails; too much can obscure rhythmic attacks. Keep important low-frequency material stable in stereo and inspect mono compatibility.

## Level and revision

Sample peak is the largest stored amplitude. True peak estimates intersample peaks. RMS is average signal energy; LUFS applies perceptual weighting and gating. They answer different questions. Do not choose a universal loudness target before the delivery context is known, and do not master just to make an unfinished idea seem more exciting.

Compare equivalent sections at matched loudness. Preserve a rough mix, state the problem in audible terms, change one thing, and judge the result. Spectrogram brightness reveals energy in a frequency/time region; it cannot tell us whether the hook is memorable. A dark region may be an intentional rest.

## Focused reference shelf

- [Ableton Learning Music](https://learningmusic.ableton.com/): interactive rhythm, scales, chords, bass and melody exercises; useful for audible examples.
- [Song structure](https://learningmusic.ableton.com/song-structure/song-structure.html): arranging patterns into sections.
- [Voicings](https://learningmusic.ableton.com/advanced-topics/voicings.html): register and distribution of chord tones.
- [Melodic variation](https://learningmusic.ableton.com/make-melodies/ride-variations.html): develop a motif by changing its placement and interaction.
- [Open Music Theory: rhythm and meter in pop](https://viva.pressbooks.pub/openmusictheory/chapter/rhythm-and-meter-in-pop-music/): beat hierarchy, backbeat and syncopation.
- [iZotope reference mixing](https://www.izotope.com/community/blog/13-tips-for-using-references-while-mixing): level matching and focused comparisons.
- [Strudel guide and DJ_Dave research](../references/strudel/README.md): practical syntax, live/export workflow, artist interviews and production demonstration.

Reference research checked 2026-10-10. The examples and practice suggestions above are our synthesis, not quotations or claims about one artist's exact process.
