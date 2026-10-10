# Modular composition in practice

The [30-second club sprint](../projects/club-detail-sprint/README.md) used separate composition, sound-design, tooling and critical-review roles. Modules made changes inspectable; they did not establish musical quality. Olof's approved heavy foundation was the common starting point, while each contender had one different organising idea.

## Agree on the piece before adding parts

Keep one owner for tempo, cycle range, shared constants and the overall arrangement. Give each sound module a defined role and a named stem; use unique labels, bindings and sample prefixes. Choose shared effect orbits deliberately. A part should answer, interrupt, expose or transform something already present. Its justification is not that more detail can be programmed.

Pressure Lock's fixed resonator family changes material while a rhythmic cell remains recognisable. Negative Space prints one original object and changes its role from whole gesture to stretched body to replies. Latch tests continuous propulsion and a common processed texture. The generators and module manifests preserve those relationships instead of treating every sound as an unrelated preset.

## Check global phase

Mini-notation sequences run in global cycles. Masking a four-cycle sequence until cycle10 does not restart it: its first active value is index2. For example, `<a b c d>` starts with `c` at cycle10. If that passage should begin with `a`, its global sequence must be aligned accordingly, or use an explicit arrangement covering the full range.

Negative Space v010 exposed this mistake; v011 corrected it. The real-export trace found three coincident bass/object attacks before the fix and none after it. Separation was that passage's intention, not a universal rule that simultaneous attacks are wrong.

```sh
uv run --locked python music.py render ASSEMBLED_SOURCE --end END_CYCLE \
  --samples LOCAL_SAMPLE_FOLDER --solo sub --solo ghost --trace-events --out NEW_OUTPUT
```

`events.json` records onsets returned during the exporter's actual queries. It does not add independent queries, and its dry-audio parity is tested. Inspect the primitive controls and cycle positions to understand the pattern. Then inspect the rendered audio: note gates, sample envelopes, effects and perceptual masking differ from event positions.

## Keep experiments comparable

Preserve each candidate before editing. Reuse unchanged module paths where convenient; assemble snapshots before rendering. Keep raw masters and aligned stems, check PCM rails before attenuating, and match comparable excerpts for listening. Rendering a section afresh can change its preceding effect state; extract a preview from the completed master instead.

Use deterministic generators for original assets and retain printed sound objects when they become inputs. A fresh rebuild can verify asset hashes and source assembly while the wet audio still varies slightly. Record that limit rather than promising identical sound bytes.

Audio-model comments are hypotheses. This sprint's short duplicate control elicited invented tonal differences; narrowing the question did not solve the problem. Use source/event evidence for timing, waveform evidence for technical defects and human listening for groove, identity and taste. See [listening protocol](listening.md).
