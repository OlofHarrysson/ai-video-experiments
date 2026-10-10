# Negative Space

A 30-second original club miniature at 128 BPM. Heavy bass and broken percussion surround one hollow dub object: it appears whole, expands into a pause, returns as uneven rhythmic fragments, then resolves into a final bloom. Its identity comes from sound, timing and space, with no foreground tune or moving chord progression.

This is direction B in the two-hour composition sprint requested on 2026-10-10. Olof approved Undertow's bass-heavy sound but wants greater craft, detail and originality. No human verdict on Negative Space has been received.

## Inspect the work

- Selected version for Olof’s listening: `renders/v012/master/render.wav`.
- Earlier stable alternative: `renders/v007/master/render.wav`.
- Expressive alternatives: `renders/v008/master/render.wav` and the tighter hybrid `renders/v009/master/render.wav`.
- Earlier, simpler alternative: `renders/v004/master/render.wav`.
- Each render directory contains separate drums, bass, dub and edits stems, source snapshots, engine/sample hashes and audio inspection results.
- `reviews/audition-v007-v008/` compares the 10–26 second passage; `reviews/audition-v007-v009/` compares the first 29 seconds. Both are anonymous and loudness-matched. Model preferences favored v007, with important interpretation limits below.

V011 measures exactly 30 seconds at 48 kHz stereo, −17.15 LUFS and −3.06 dBTP, with zero PCM rail samples. Its final 100 ms peak is −64.29 dBFS. The new return makes bass attacks and object answers alternate explicitly and removes the spring layer there. This is a compositional choice, not a human or model approval.

V007 measures exactly 30 seconds at 48 kHz stereo, −17.08 LUFS and −2.86 dBTP, with zero PCM rail samples. Its final 100 ms peak is −63.86 dBFS. V008 and v009 also have zero rails and roughly −17.07 LUFS / −2.86 dBTP. These are technical checks, not proof of musical quality. The master is deliberately close to mono because kick and bass dominate the centre; the texture stems retain stereo motion.

## Arrangement and sound

| Time | Musical role |
| --- | --- |
| 0–3.75 s | Establish the rolling bass and whole hollow object, with space around its attack. |
| 3.75–7.5 s | Hats and clap enter; the object answers from a different position. |
| 7.5–15 s | Full groove and a differently placed response. V008/v009 explore a delayed bloom here; v007 keeps the original sharper articulation. |
| 15–18.75 s | Bass and kick thin out to sparse pulses; the slowed bloom and filtered tail occupy the exposed room. |
| 18.75–26.25 s | Held bass notes and changed kick placement return. V011 uses four distinct bass/object exchanges; the object answers the bass gaps and the spring layer withdraws. V007 retains its earlier rolling-bass callback. |
| 26.25–30 s | A deep impact and whole object release into the ending. V008/v009 use the softer blooming articulation. |

`assembly-v012.json` owns the selected module and stem assignments. It reuses the v011 setup, drums, bass and edits, and changes only the dub module in `modules/v012/`. The assembly output in `assemblies/v012/` is the selected candidate’s reproducible project recipe and source. V008/v009 have equivalent preserved module and assembly folders. Root `project.json` and `source/v001.strudel` preserve the original first draft; they do not represent the latest version.

## Original palette and provenance

All special sounds are deterministic synthesis or transformations of our own printed material. Retained 909 drum assets live in the sibling `practical-dogfood` project's recorded sample collection. No speech, third-party song recording or DJ_Dave audio is incorporated.

- `make_palette.py`: original struck spring, low servo response, sharp unresolved chord, stereo friction grains, reversed chord and closing sub impact. The servo and initial chord are preserved but no longer used in v008.
- `make_cloud.py`: a softer F–Ab–C–Eb chord with detuned partials, a softened onset and a bright-to-dark decay. Played at 0.75 speed, it provides a stable suspended colour over the F bass.
- `capture_ghost.py`: early composite-tail experiment from v001. It includes direct chord tail, an echo layer, delay and reverb; it is not an isolated effect return.
- `capture_bloom.py`: the whole v004 dub gesture, preserved as `nsbloom` and its reversed counterpart.
- `source/body-probe.strudel` and `capture_body.py`: a new print with less high-pass filtering before capture, preserving the object's evolving low-mid body as `nsbloomwarm`. The source window is 0.703125–2.578125 seconds.
- `perform_object.py`: v008's `nsbloomrise` articulation of that same print. Capped envelope shaping moves its measured RMS peak from roughly 30 ms to 193 ms; a low-pass blend opens with the body and darkens again. It adds no oscillator or external recording.

`references/*.json` records sample hashes, source windows, processing and origins. Assets and raw renders are local and ignored by Git; the scripts and provenance are tracked. Preserve the local assets with the project when moving it.

## Reproduce

From `apps/music`, with the recorded local sample assets present:

```sh
uv run --locked python music.py assemble projects/negative-space/assembly-v012.json --out projects/negative-space/assemblies/v012-rebuild
uv run --locked python music.py render-project projects/negative-space/assemblies/v012-rebuild/project.json --revision v012 --out projects/negative-space/renders/v012-rebuild --timeout 180
uv run --locked python music.py analyze-project projects/negative-space/renders/v012-rebuild --out projects/negative-space/reviews/analysis-v012-rebuild --window-cycles 1
```

The sample generators refuse to overwrite original assets. If rebuilding the current custom palette from scratch in a separate copy, run `make_palette.py`, then `make_cloud.py`; render `source/body-probe.strudel` for cycles 0–2 with `references/assets/samples`, run `capture_body.py`, then `perform_object.py`. Older `nsghost` and `nsbloom` assets are needed only for historical versions. The recorded sibling drum folder must also be present.

## Revision and review evidence

| Version | Decision |
| --- | --- |
| v001 | First complete render. Audio-model request timed out; provider outcome and cost remain unknown. |
| v002 | Foreground raised and composite tail resampled. Rejected: the new PCM rail detector found seven clipped samples. |
| v003 | Source-level headroom fixed clipping. Review described overly sharp objects; its claim that every phrase was identical conflicts with the source. |
| v004 | Softer original chord, reduced servo, changed return bass/kick. A loudness-matched v003/v004 model comparison preferred its rounder, darker sound; it also described muted top end. Preserved as an earlier alternative. |
| v005 | Whole printed gesture becomes chopped return; servo removed. Comparison review falsely claimed an entire candidate was time-reversed. Direct waveform checks disproved that claim; its preference is discarded. |
| v006 | Object attack moves between kick and bass; unequal slices and a brief return of the rolling bass create stronger phrasing. |
| v007 | Less high-pass filtering in the source print preserves low-mid body. Whole object sits roughly 6 dB below the mix in its body band when present, versus roughly 10 dB in v004. Band levels are not perceptual audibility scores. |
| v008 | Same family gains a blooming articulation, four distinct slice responses and changing echo feedback. Model comparison preferred v007’s tighter rhythmic focus; retain this as a more sustained alternative. |
| v009 | Hybrid keeps the blooming first-half/ending gestures while restoring v007’s vacuum and return. Model again preferred v007, but incorrectly generalized envelope differences across passages whose source is unchanged. Its literal timeline is not reliable. |
| v010 | Four-bar return places longer bass notes and chopped object answers into complementary gaps and removes the competing spring layer. Pinned-engine event inspection caught a global-cycle phase mismatch: three attacks still coincided. Preserved as the intermediate experiment. |
| v011 | Correct phase alignment at cycle 10. Three/two/four/two bass attacks receive three/three/two/four object answers across four different bars. Zero bass/object onset coincidences in this deliberately separated exchange; this is not a universal composition rule. Opening, vacuum and ending retain v007. No new model review. |

## Final reply dynamics

V012 retains v011's whole arrangement and all twelve chopped-reply timings, but lifts slice type 2 by 3 dB and the quietest tail slice type 3 by 7 dB. The main slice attacks retain their original gains. Solo renders show the tail replies remain roughly 9–14 dB below principal attacks; the whole return dub stem rises only about 0.25 dB. This preserves accent hierarchy while giving the tail fragments a stronger signal. Master loudness/true peak remain −17.15 LUFS / −3.06 dBTP, with zero rails and aligned 30-second stems.

The actual-export traces have identical timings, durations, bounds and all non-gain controls. Short onset measurements include preceding effect tails; they are not isolated-sample loudness or perceptual scores. [Repeatable dynamics audit](../club-detail-sprint/audit_reply_dynamics.py) and [evidence](../club-detail-sprint/reply-dynamics-study.json) preserve the comparison. The v012 portable bundle was rebuilt successfully with identical source/sample hashes and sample indices, and clean aligned master/stems. V011 remains the prior selection. No additional paid review was used for this refinement.

## Reproduction and return audit

`audit_reproduction.py` rebuilds ten original assets in a fresh temporary project and checks each byte hash. All ten match. The captured object starts from the preserved `renders/body-probe/render.wav`; it is a source asset in this chain, not a claim that WebAudio reverb can be regenerated byte-identically.

The same audit verifies the master and all four stems for v007, v009, v010 and v011 plus a freshly assembled/rendered v007: 1,440,000 frames each, 48 kHz stereo, zero PCM rail samples, source/output/sample hashes valid. `reproduction-audit.json` records exact hashes, ending peaks and mono fold-down measurements. The fresh v007 render matches rounded master LUFS and true peak, but audio bytes differ; the edits stem changes by −0.35 LUFS and +0.06 dB true peak. Preserve selected audio alongside recipes rather than promising byte-identical rendering.

`audit_return.mjs` queries the actual pinned browser bundle without rendering sound, reads the selected bass/object layers, and saves their global cycle positions in `return-events.json`. It confirmed the phase error in v010 and its correction in v011. This verifies written timing, not perceived groove. `reviews/audition-v007-v011/` contains a loudness-matched 18.75–26.25 second comparison for listening; it has not been sent to an audio model.

Known completed review cost is $0.134812, plus the v001 request whose outcome/cost is unknown. Requests and raw reviews are preserved locally under `reviews/`; `evidence-progress.json` holds the tracked technical summary. Audio-model descriptions are hypotheses, not personal listening or expert approval.

## Reference technique

[El Choop's Ableton interview](https://www.ableton.com/en/blog/designing-dub-chords-in-ableton-live-with-el-chooppizza-hotline/) informed processing returning echoes differently from the source and moving the timbre around a stable chord. Independent analysis of the official demonstration samples supported varying attack/body relationships: some hits bloom later instead of simply becoming brighter. These are production references; no demonstration sample was added to this track.
