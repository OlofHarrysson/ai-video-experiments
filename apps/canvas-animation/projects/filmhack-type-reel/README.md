# Filmhack type reel

A ~20-second vertical Instagram Reel that recruits filmmakers to [Filmhack](https://filmhack.ai/) (Nov 13–15, 2026, Filmuniversität Babelsberg). Typography is the main image: high energy, bold and visually sophisticated, with rhythmic bursts, short breaths and clear punctuation. This is a new project; the earlier [promo reel](../filmhack-promo/README.md) and [title-sequence study](../title-sequence-study/README.md) are evidence, not templates.

## Decisions so far — 2026-10-10

| Topic | Decision | Source |
|---|---|---|
| Purpose | Recruitment promo: excitement and FOMO before the Oct 24 application deadline | Olof |
| Screen | Instagram vertical feeds, 9:16 | Olof |
| Audience | Classic filmmakers on the fence about AI | Olof |
| Feeling at the end | Hyped together; fun, and impossible to miss | Olof |
| Duration | About 20 s, flexible | Olof |
| Sound | Original track composed in the [music workbench](../../../music/README.md) (Strudel) first; picture cut to it | Olof |
| Posting account | Undecided; the end card must work from either account | Olof |
| Direction | **A · doubt vs answer**, chosen tentatively. Olof: graphic quality is the priority; the timing animatic is ugly | Olof |
| Comprehension | The opening must be understood in one glance | Olof |

Rejected or parked: credit-list concept (too slow to read without a frame), "This film needs a ___" (may join A as one answer), "ACTION!" (offer lands late).

## Direction A in one line

The voice in a filmmaker's head talks them out of applying; the film answers back louder each time, until the doubts are drowned out by a chorus.

- [Script and rhythm outline v1](script.md)
- [Reference study](references.md): five excerpts, measurements and what each contributes
- Timing animatic of three openings: `renders/animatic-openings-v001.mp4` (placeholder look; rebuild with `uv run --script tools/animatic.py <out_dir>`)

## Status

Script v1 approved for keyframe design. Round 1 visual targets generated (2026-10-10): eight keyframes on `openai/gpt-image-2.5-sunburst` (high) and `google/gemini-nano-banana-2.1` (2K), plus two SVG tests on `recraft/recraft-v4.1-pro-vector`, from [these prompts](targets/prompts-round-01.json). Olof authorized up to $10 of OpenRouter spend; round 1 reported $1.30 in usage (the account balance had moved $0.82 when checked). Outputs, hashes and exact prompts are in ignored `references/targets/round-01/` (`manifest.json`, `shortlist-round-01.jpg`, `compare-*.jpg`).

Assistant screening: Sunburst is strongest for YES, the marquee, woven crew, film-strip and chorus; Nano Banana's contour version suits CONSTRAINTS. All lettering is spelled correctly. Sunburst returned 864×1536 images. Risk: most targets share a glossy, rendered-3D look; the references also rely on flat, sharp graphic identities, so the set needs flatter contrast. Awaiting Olof's selection.

Next: Olof selects identities → editable reconstruction → motion proof of the first three doubt/answer pairs → review before the full Reel.

## Files

- `tools/`: reference analysis (`sheet.py` contact sheets, `changes.py` frame-change classes, `rhythm.py` and `sound.py` beat/onset/spectrogram) and the animatic renderer. Run with `uv run --script`.
- `references/` (ignored): inspection sheets of the reference films. Reference pixels stay local.
- `renders/` (ignored): animatics and renders.
