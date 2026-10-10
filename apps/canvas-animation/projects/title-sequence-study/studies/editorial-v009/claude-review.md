# Claude design consultation

2026-10-10. Read-only consultation through Claude Code 2.1.280, Opus high effort. Resolved model: `claude-opus-5-5`. Reviewed candidate stills and source; no video existed yet.

**Takeaway:** your eight are close. I'd change one slot and make one correction that runs through the whole set. I'd swap **giant → small**. The cross-cutting problem is more important than the selection: every card is a full-frame, flat, multi-colour lockup of the whole phrase, and 13 of the 20 lean on the same Cormorant italic. That single fact explains most of the "polite" feeling.

I've only seen still frames. Everything I say about motion comes from reading `art.js`, not from watching anything.

## What the references do that our cards don't

- **One idea per card.** Each Enter the Void name card is one face, one treatment and one colour family, and any secondary text is small and practical. Ours stack the main word, a serif secondary, rails, stars and stripes.
- **The letters give off light.** Nearly every reference card has a glow around neon on black. Ours look like crisp print: chrome stripes and gradients instead of light. This is the biggest gap in visual quality.
- **Size changes.** All of the Lights moves between a tiny "UP" or "KNOW" lost in black and a cropped ".IGH" filling the frame. Nineteen of our twenty cards fill about 90% of the width, so no rhythm can come from size.
- **The copy changes.** In the references the words change from card to card. Ours repeats the same phrase eight times, which turns the cut into a font carousel.

## My selection, with the fixes worth making now

| Slot | Pick | Fixes |
|---|---|---|
| Impact | **01** | The double rule strikes through the IT (`art.js:49-50`). Move it below the IT or delete it. This is the one place the serif earns its place, as a single interruption. |
| Chrome | **03** | Remove the 5px scanline hatch inside the metal (`:76-77`); it reads as gradient banding when small. Replace the scattered MAKE/IT labels (`:84-85`) with one tracked "MAKE IT" line aligned to the M's left edge. Also check the inner counter of the E; I think the extrusion shows through there. |
| Lamps | **12 (wall)** | **Legibility bug:** the travelling dark column (`:168`, `x/65` bands) falls inside the M, and the contact sheet reads **"IMOVE"**. Dim whole letters instead: the All of the Lights "THIS" card does exactly this, with a dim H. Add a glow, and move the "it" off the E. |
| Tunnel | **09** | The layers scale toward a fixed corner (75,154) (`:139`), so the result looks like a smeared offset rather than depth. Scale around the word's centre, like the NOBUMAI and OLLY cards. Cut 25 layers to about 10 and use one hot colour plus cream. "MAKEIT" has no visible space (`:149`, gap 120 is too small). Increase the gap or drop the label. |
| Gothic | **07 composition, new treatment** | It currently uses the same striped metal gradient as chrome (`:123-125`), so it reads as the 80s-airbrush material twice. Make it flat cream or lavender with a violet glow, like the Lucile/Cyril Roy cards. 07's blackletter "it" is better than 08's floating serif. Accept "Mafe": the blackletter k is real to the period. |
| Split | **13** | Remove the three vertical voids (`:191-192`); they split the E and add a third system. Consider lime-only slats with black gaps, closer to the All of the Lights "THE" card. Set "it" in the slat construction or remove it. |
| Optical | **15** | Remove the pink serif "Make it" (`:207`). Use two colours plus a rare red ring. The rings grow only about 10px per shot (`:205`), less than one ring spacing, so they will look static. Move them through one or two 39px colour periods. |
| Scale | **17 (small)**, not 18 | See below. |

## Pushback

- **Giant:** as built, it's the polite serif lockup over a purple slab M, and impact-oblique (02) already covers the cropped-slab idea. It also doesn't use `p` at all (`:214`), so it's a still image. The set has no negative space, and **small** supplies it: a 9–12 frame breath, like "UP" and "KNOW". If you want a giant card anyway, rebuild it as a 6–9 frame punch: a single cropped glyph in one flat colour with no phrase.
- **Strongest omission:** razor-solid (20). It uses a genuinely different construction, custom polygons, and sits near the All of the Lights "FAST"/"CARS" cards. It's a good alternate if gothic doesn't improve.
- **Process:** before cutting, give each card a hero word. Some cards say only MOVE, some only MAKE, and two or three carry the full lockup. That one change does more for rhythm than any further card polish.
- **Glow:** add an opt-in bloom per card. Redraw the card with `filter='blur(10px)'` and `'lighter'` at about 0.5 alpha, for lamps, tunnel, gothic and optical only. Leave impact and split flat.

## A starting rhythm (288 frames, no acceleration)

impact 36 · lamps 15 · chrome 42 · split 12 · tunnel 42 · small 12 · gothic 30 · optical 39 · lamps 12 · chrome hold 48

Long and short cards alternate, the short ones never get shorter, and it ends on a held anchor instead of a flurry. Chrome's light sweep needs at least 40 frames to read.

I didn't modify anything. These are directions for whoever implements the next pass.

## Application

Adopted: reduced repeated italic supporting copy, changed the scale slot to the tiny IT card, removed heavy chrome hatching and extra split-card cuts, made blackletter ivory/violet rather than another metal material, changed lamp dimming from arbitrary columns to letter-sized regions, simplified tunnel colour/layer count, expanded optical travel and added selective bloom.

The proposed roughly 1–2-second holds were not adopted: Olof previously rejected slow starts and prefers sustained medium-high activity. The selected cut uses 0.25–0.875-second shots with no escalation. The blanket claim that nearly every reference frame glows is too broad; our inspected reference sheets also contain sharp flat graphics. Bloom remains restricted to actual light treatments.
