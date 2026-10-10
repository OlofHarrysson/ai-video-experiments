# Thirty-second club studies

Two selected excerpts from Olof's two-hour composition and tooling sprint on 2026-10-10, run from 12:10:53 UTC through the two-hour target of 14:10:53 UTC. The final handoff was recorded at 14:11:28 UTC. The brief was to push craft, detail and identity beyond Undertow while preserving its approved heavy bass/drum direction. Human listening judgment on these selections is pending.

- **[Pressure Lock v011](../pressure-study/README.md), 136 BPM.** A shifting mechanical rhythm changes from metal into elastic low body, then returns inside the groove in a darker form. [Play selected copy](exports/selected-v002/pressure-lock.wav).
- **[Negative Space v012](../negative-space/README.md), 128 BPM.** One hollow dub object appears whole, stretches into an exposed passage and returns as four deliberately different bass/object exchanges. [Play selected copy](exports/selected-v002/negative-space.wav).

Both are exactly 30 seconds, including their endings, at 48 kHz stereo. Listening copies are matched to −17.15 LUFS using only constant attenuation. No compression or time stretching was added. The raw masters have zero PCM rail contacts. See [delivery evidence](delivery-evidence.json) and [selection reasoning](selection-notes.md).

[Latch v006](../latch/README.md) is the preserved third contender: continuous propulsion, friction calls and burred bass responses, using room-before-saturation processing. Each contender developed through separately owned composition/sound-design work and independent criticism. All unique revisions, original generators, source modules and render evidence remain preserved. This is an assistant selection for Olof to assess, not an established professional-quality verdict.

## Tooling exercised on actual compositions

- **Modular assembly:** one arrangement owner, independently editable sound modules, checked label/binding ownership and exact source snapshots. Dry assembled audio matches equivalent monolithic source byte for byte.
- **Stem/band inspection and matched comparisons:** time-resolved measurements expose energy changes; randomized A/B pairs hide revision names. Neither provides a taste score.
- **Clipping checks:** positive PCM rail detection caught overloaded revisions that earlier absolute-level checks missed. Source levels were corrected before selection; render summaries now surface rail and true-peak warnings.
- **Actual export event traces:** an observed global-cycle phase error caused three unintended bass/object collisions in Negative Space v010. V011 has zero in the intended exchange. The trace observes actual export queries without adding a second evaluation; it proves scheduling, not audibility or effect-tail separation.
- **Portable bundles:** both selected recipes were rebuilt using only their bundled source and sample banks. Master plus four stems completed for each, with aligned frames and zero rails. Saved audio is exact; wet rerenders vary slightly. [Bundle audit](bundle-evidence.json). A separate fresh Python/Node installation also rebuilt the final Negative Space bundle successfully; it used the existing system Chrome/FFmpeg and retained dependency caches. [Clean-install evidence](clean-install-evidence.json).
- **Review plumbing:** concurrent requests no longer hold a ledger lock through a network call; explicit model/provider evaluations retain actual transport hashes and unresolved outcomes.

Final tooling checkpoint: **36 Python tests, 16 renderer tests, none skipped, and Ruff pass**. The renderer suite includes sustained-note/global-phase tracing, cropped offsets and unchanged dry audio. [Composition workflow](../../docs/modular-composition.md) records the practical lessons.

## Preserve and continue

Editable portable snapshots are in `exports/bundles/pressure-lock/` and `exports/bundles/negative-space-v012/`. From an installed music workbench, pass its `project.json` to `render-project --revision v011 --out NEW_OUTPUT` for Pressure, or `--revision v012` for Negative Space. Original module files and sound generators stay in their owning project folders; the bundles contain assembled source, all registered sample banks, raw master/stems and provenance.

All audio and private API receipts remain local and ignored by Git. A bundle here is not a second-device backup. Negative Space's captured sound object depends on a preserved original print; do not discard it expecting identical WebAudio reverb to regenerate from a seed.

For the next iteration, use Olof's listening verdict to choose which identity to develop. Extend the chosen musical idea rather than joining all three candidates or adding layers simply because the system can generate them. Keep the 30-second selections as baselines. Focused stem previews and a v011/v012 return comparison are preserved under ignored `screening/`; [sample checks](focused-preview-evidence.json) confirm their exact extraction and gain transforms.

## Listening evidence and limits

Reference work includes first-person production techniques, El Choop's official demonstration samples and public Blawan/Surgeon previews. They were used for research and analysis only, not incorporated into these tracks. The original special-sound palettes sit over the retained 909 drum recordings. [Independent production notes](critic/production-notes.md) and [final assessment](critic/final-candidate-assessment.md) document the distinction.

Audio-model screening did not establish reliable subtle mix judgment. An exact duplicate elicited invented tonal differences, a real change was falsely described as playback reversal, and a substantial exposed low-band change was missed. Alternative provider evaluations did not establish a dependable replacement. Concrete claims were checked against source, events and audio measurements; human listening remains necessary for groove, identity and taste. [Listening evaluation](listening-evaluation.md).

The sprint records 35 completed review responses with **$0.7184919 reported usage**, plus two timed-out requests with unknown provider outcome/cost. No automatic retries or model fallback were added. Olof controls account funding; these figures are accounting, not a spending cap. [Request accounting](review-accounting.json).
