# Independent candidate assessment

Scope: preserved sources, arrangement intent, render receipts, local waveform measurements and provenance. These findings do not claim direct hearing or establish human taste. Audio-model preferences are not used as decisive evidence: a recent exact-duplicate control elicited invented tonal differences.

## Selection advice

Pressure v011 is the strongest source-level choice for the first slot. Its five-step rhythmic object changes material while retaining its timing, then carries that change into the returning groove. The fixed resonator bank avoids the earlier pitch-descent experiment's risk of turning the object into a prominent melody. Recommend Negative Space v011 for the second slot: its returned bass and object are now written as a coordinated four-bar answer, giving the resampled material a clearer rhythmic purpose. Latch v005 remains the meaningful continuous-groove challenger. This is a selection based on the brief, source relationships and verified technical behavior, not a claim that either track has passed human taste judgment.

| Candidate | Specific identity and development | Remaining structural risk |
| --- | --- | --- |
| Pressure v011 | Five-sixteenth cell shifts against the bar; upper resonances shorten while lower body lengthens; exposure around 11.5–14.1 s; object returns with the core groove in a changed state | The latter groove still needs its timbral change to carry the identity. More source detail does not guarantee a memorable sound. Avoid reintroducing high pitched runs to satisfy model praise. |
| Negative Space v007 | Whole original dub object appears in alternate bars, is slowed in the central vacuum, then returns as uneven slices against longer bass notes | Shares an exposure/return outline with Pressure. The returned slice pattern alternates two bars twice; this is a stable motif, not evidence that the whole arrangement is unchanged. |
| Negative Space v009 | Keeps v007's vacuum and sliced return; changes one earlier whole-object articulation and the closing hit into a bloom, with some earlier pan/filter variation | A focused articulation variant rather than a new arrangement. Do not describe it as substantially more developed than v007 without human evidence. |
| Negative Space v011 | Preserves the initial whole object and vacuum; a new four-bar return places 12 sliced-object attacks between 11 bass attacks, with the earlier spring pattern removed from that return | Still uses the same large exposure/return outline as Pressure. Scheduled separation supports the design but does not prove the sound is perceived as a compelling dialogue. |
| Latch v005 | Continuous low groove, sparse individually placed friction calls and rough bass replies; common room printed before saturation into both original objects | Almost every foreground bar differs, so recognizable rhythmic recall is less explicit than Pressure's cell or Negative Space's repeating cue. Two call/reply onsets coincide near three quarters of cycles 2 and 9; those can be deliberate punctuation, but not every event is separated. |

Latch v003 was also audited as a preserved predecessor. V005 is a substantive structural alternative to it: the central low-end suspension is removed, and the new phrasing replaces free-running foreground patterns. Its source-wide 0.8 postgain means raw loudness comparison against earlier versions would be misleading.

Repeating a motif is not a weakness by itself. All candidates retain an intentionally stable F-centered foundation. The useful distinction is whether returning material has a clear relationship to what preceded it, rather than whether every bar contains a new event. Pressure's five-step phase and Negative Space's whole-to-slice sequence provide explicit relationships; Latch relies more on its shared material, sparse exchanges and uninterrupted propulsion.

## Technical audit

All six audited versions (Pressure11, NegativeSpace7/9/11, Latch3/5) have matching source, output and inspection hashes; matching hashes for every registered sample; aligned master/stem frames; no reported render errors; and zero PCM rail samples. Registered banks can contain unused sounds, so this is not a count of audible layers.

| Candidate | Duration | LUFS | True peak | Mono RMS loss |
| --- | ---: | ---: | ---: | ---: |
| Pressure11 | 30.000000 s | −14.42 | −1.00 dBTP | 0.012 dB |
| NegativeSpace7 | 30.000000 s | −17.08 | −2.86 dBTP | 0.009 dB |
| NegativeSpace9 | 30.000000 s | −17.07 | −2.85 dBTP | 0.010 dB |
| NegativeSpace11 | 30.000000 s | −17.15 | −3.06 dBTP | 0.008 dB |
| Latch3 | 29.999979 s | −14.83 | −0.46 dBTP | 0.005 dB |
| Latch5 | 29.999979 s | −16.59 | −2.16 dBTP | 0.036 dB |

Pressure's last 100 ms peak is approximately −84 dBFS. Both Latch versions finish at digital zero. Negative Space7/9 retain a very quiet tail in the last 100 ms (peaks approximately −64/−62 dBFS, last sample approximately −76 dBFS); this is not a substantial hard cut. Negative Space11 also has a quiet tail (last 100 ms peak −64 dBFS; last sample approximately −81 dBFS). A very short final delivery fade can make the endpoint exactly zero if desired. Latch's one-frame difference from thirty seconds is immaterial. These checks establish file integrity and gross level behavior, not sonic quality.

Full numerical evidence: `candidate-audit.json`.

For Negative Space11, the actual exporter trace confirms 11 bass and 12 sliced-object scheduled attacks in cycles 10–14, with zero coincident onsets and zero object attacks strictly inside a scheduled bass gate. The trace uses a solo evaluation of sub/ghost, so its evaluated-source hash differs from the full master; its original-source hash matches the master exactly. Both links were checked. Effects, releases and printed sample tails can still overlap; scheduled gates are not a claim of silent gaps. See `negative-v011-timing-audit.json`.

## Provenance and review accounting

The new palettes come from retained deterministic synthesis scripts and, in Negative Space/Latch, documented processing of their own original printed objects. The drum origin is separately recorded in `projects/practical-dogfood/drum-sources.json`; the complete tracks should not be described as containing only newly synthesized audio. The El Choop samples and Blawan/Surgeon public previews used for research remain local analysis references under ignored `.local/`; none appears in these candidate sample chains.

Of 52 selected asset/source/generator provenance checks, 51 match their recorded hashes. Pressure's base `make_palette.py` has a different byte hash from its historical receipt. An isolated regeneration using the current script reproduced all 16 original assets exactly. Thus the source still reproduces the audio; the old generator-byte receipt is stale. The original receipt and the independent verification are both preserved in `pressure-generator-reproduction.json` rather than silently changing historical evidence. Other checked chains pass; see `provenance-audit.json`.

The critic's eight paid review receipts reconcile exactly to **$0.169062**, with zero unknown outcomes. This is only the critic-owned subset; composer and parent requests, including their timeouts, must be counted separately. No new paid calls were made for this audit. The failed focused short-review experiment is documented in `short-review-calibration.md`.
