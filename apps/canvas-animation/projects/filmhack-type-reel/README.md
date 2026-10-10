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

Assistant screening: Sunburst is strongest for YES, the marquee, woven crew, film-strip and chorus; Nano Banana's contour version suits CONSTRAINTS. All lettering is spelled correctly. Sunburst returned 864×1536 images. Most round-1 targets shared a glossy, rendered-3D look, so Olof chose to add flat graphic contrast: round 2 ([prompts](targets/prompts-round-02.json), $0.53 reported) produced the hairline thread, cut-paper ROUGH CUTS, dot-matrix FREE, seat-chart FULL HOUSE, striped dates and striped end card. The working storyboard is `references/targets/board-v001.jpg` (built by `tools/board.py`). Model artifacts to correct in code: stray slashes in "/BEAT/" and "FULL / HOUSE".

### Motion proof v001 — 2026-10-10

[proof-v001/](proof-v001/) renders bars 1–3 (6.0 s, 1080×1920, 30 fps) with a scratch 140 BPM beat. Olof chose a **hybrid build**: code-native cards where motion lives in the letter construction, generated-image layers animated in code where the material is the point.

| Card | Construction | Motion |
|---|---|---|
| Doubt | Cormorant Garamond Italic, hairline rule, cursor | Types on; crushed by YES; its rule becomes the thread |
| YES. | Sunburst chrome target as an image layer with a luminance letter mask; Anton flat identities | 2 frames flat crimson → 2 frames cyan inline → chrome slam with spring; light band travels through the metal; cyan accent flip on the next beat |
| NO AI EXPERIENCE NEEDED | Anton outlines, Clipper-inset bulb channels, panels, neon shield, crown fan, deco sunburst, stars | Builds itself in ~0.4 s; chasing border bulbs; letter bulbs flash on the following beats; two-pass glow |
| MOST PEOPLE COME ALONE. | Hershey single-stroke skeleton | One hairline thread rises from the doubt's rule and writes both lines |
| CREWS FORM FRIDAY | Same skeleton type; three strands braided by phase-sorted depth | Ivory lead thread, then crimson, cobalt and gold strands join one by one; the braid keeps flowing |

Render: `npm ci && node render.mjs output-NN [--movie]` from `proof-v001/` (Playwright from the Animate skill). Outputs are ignored and never overwritten; `output-03/` is the reviewed version (`proof.mp4`, stills, `contact.png`, dense screening sheets, `target-vs-code.jpg`, `report.json` with source hashes).

Assistant screening of the decoded MP4: deterministic rendering, no page errors; every frame inspected around the YES landing, marquee build, thread and braid. Only three large-area brightness jumps, all cuts ≥0.7 s apart (within the ≤3 flashes/s guideline). Fixed during screening: blown-out marquee bulbs, a mistimed YES accent, and a thread lead that read as a strike-through.

Known gaps against the targets: YES matches closely (image layer); the marquee is simpler, with less ornament and narrower letters; CREWS is the weakest reconstruction — thin single-stroke skeletons give braided-yarn letters instead of the target's broad flat ribbons and gold foil. The chrome S extends into Instagram's lower UI zone. The scratch beat only marks timing; the assistant cannot listen.

Next: Olof's motion review → strengthen CREWS (bolder skeleton, broad flat ribbons, foil) and marquee ornament → compose the Strudel track → extend through the chorus and end card.

## Files

- `tools/`: reference analysis (`sheet.py` contact sheets, `changes.py` frame-change classes, `rhythm.py` and `sound.py` beat/onset/spectrogram) and the animatic renderer. Run with `uv run --script`.
- `references/` (ignored): inspection sheets of the reference films. Reference pixels stay local.
- `renders/` (ignored): animatics and renders.
