# Professional sample reference

The [official Ableton interview with El Choop](https://www.ableton.com/en/blog/designing-dub-chords-in-ableton-live-with-el-chooppizza-hotline/) provides a [19-sample chord download](https://cdn-resources.ableton.com/resources/misc-downloads/el_choop_stabs.zip). Downloaded 2026-10-10 for local analysis. The archive, original samples and hash manifest are retained under `.local/el-choop-reference/`. None of this audio was added to our compositions or republished.

This extends the text research with actual waveform measurements. It is not an audition of his released tracks, nor a benchmark proving that a particular envelope sounds professional.

## Findings that affected the work

| Raw sound | Time within 20 dB of its maximum 20 ms RMS envelope | Spectral centroid, early 20–70 ms → 200–400 ms |
| --- | ---: | ---: |
| Our original `nschord` | 0.44 s | 479 → 446 Hz |
| Our revised `nscloud` | 0.60 s | 502 → 296 Hz |
| El Choop Helm C♯m Stab 02 | 0.62 s | 893 → 261 Hz |

The revised cloud has a changing balance of harmonics through its decay, unlike the more uniform original chord. One professional example shows the same direction of change, with a brighter opening. These samples use different pitches and processing, so the values are descriptive rather than targets to match.

El Choop's Yamaha PSR-36 C♯m Stab 04 offers a different articulation: the level blooms over roughly 0.3 seconds before declining. The pack therefore does not support a blanket rule that every useful dub object needs a sharper attack. This suggested giving related objects different attack/body relationships rather than making all hits louder or adding more reverb.

The sound designer received these findings, including a caution that replaying `nscloud` at 0.75 speed and then high-passing at 430 Hz may remove much of its evolving lower body. A lower cutoff can be tested while retaining space below 180 Hz for the foundation; it is a candidate experiment, not an automatic mix improvement.

Local plot: `.local/dub-reference-envelope.png`. Numerical report: `.local/dub-reference-comparison.json`. Mono channel averaging, 20 ms RMS envelopes and STFT centroids were used. The plots normalize each sample's envelope separately. Source-specific pitch, initial silence, stereo cancellation and prior processing limit direct comparisons.
