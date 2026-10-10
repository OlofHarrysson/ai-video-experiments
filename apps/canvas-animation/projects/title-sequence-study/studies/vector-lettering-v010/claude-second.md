# Second read-only critique

Claude Opus 5.5, high effort, 2026-10-10. Read contact sheets and sampled decoded frames of motion 04, not continuous playback. This is independent model critique, not Olof approval.

**Verdict:** this is a real step forward in the lettering, but only a partial one in the edit. Next to v009's stock fonts with filters, v010 has drawn letterforms with real construction. Yet the cut still plays as **four polished logos taking turns, centred on black, at about half-second cadence**. The remaining gap to Enter the Void and All of the Lights is mostly editorial now, not material. I checked the contact sheets plus decoded frames 2, 82, 122, 159, 220 and 228. I didn't watch playback.

## What improved (judged from frames, not taste)
- **The best frames are the flat, graphic ones.** The misregistered Tuscan WILD (frame 228) is the strongest card in the cut: bold, two-colour and printed-looking. It's the closest thing here to the reference vocabulary. The wire planes (220), lime flat crops, the diamond counter and the red silhouette also work.
- **The liquid crops now read correctly.** Fixed bands and inward flow give a coherent contour rhythm.
- **The enamel hero (82) is the best-rendered frame**, with a visible gold rim and directional light. It's also the most "AI illustration / logo reveal" frame in the cut, which is the opposite register from the references.

## Why it still isn't at the reference level
1. **Cadence.** Shots run 4–30 frames, with a median of 12 (0.5 s). Your own `reference-study.md` observed replacements every 1–2 frames, plus dimmed and black frames in between. Nothing in this cut replaces a layout faster than 4 frames, and there are no black or dimmed beats.
2. **The first half is grouped by identity.** In `edit.js`, the first ~6 s are machine ×3 → liquid ×2 → script ×3 → Tuscan ×4. The hybrid and wire shots only arrive after that, so the "logos taking turns" problem is still built into the structure.
3. **Too many lockups.** Ten of 23 shots are centred whole-lockup or single-row readings at similar scale. Layouts never sit off-centre, and identities only overlap in the hybrid shot.
4. **Verbatim repeats.** Only 166 of 288 frames are unique. The assembly (0–17 → 236–251) and the contour crop (34–47 → 178–191) replay pixel for pixel, and the closing hero reuses the 2.92 s enamel shot. That makes 12 s feel like a looped 7 s reel.

## Visible defects
- **Shutter blur (frame 2).** Four additive samples at 25% alpha make stepped ghost copies, like Flash-era motion trails. My recommendation is to drop the blur and hard-step the assembly (pieces jump frame to frame instead of sliding smoothly), which also suits the reference. The alternative is 12+ samples.
- **Orange hairline on the machine D.** It's in every machine material shot and reads as a scratch or render bug. Remove it, or make it a thick deliberate rule.
- **The hybrid is the weakest shot.** The WILD fill is small hollow rings (about 12 px pitch) clipped at the letter edges, with a hairline mask outline around it. That reads as a pattern fill, not dot construction. HOURS is a 1–2 px cream hairline, WILD becomes illegible where they overlap, and the scan column looks like a UI selection. In the reference, the dots *are* the letter.
- **Wire:** per-part polygons expose internal seams, like the spikes inside H and U. Echoing the merged letter outline would read as designed contours instead of a wireframe glitch.
- **Tuscan lockup (122):** the hatching is still a uniform fringe, and the red+blue double contour runs around every edge, which gets busy at full scale. The isolated HOURS has doubled red lines in the O and the S tail.

## What to do in the ~80 minutes left, in order
1. **Re-edit in `edit.js` only (~25 min). This is the biggest lever.**
   - Interleave identities from the first second.
   - Add one 2–3 s strobe passage: same lockup position, swapping mode every 2 frames (red flat → registration → wire → enamel), with occasional dimmed or black frames, as in the reference's 2681–2685 window.
   - Cap whole lockups at about 5.
   - Make every repeat differ in crop, ink or mode.
   - Keep the long enamel hold as the contrast at the end.
2. **Kill the shutter blur and the orange hairline (~5 min).**
3. **Make the Tuscan mainly the misregistered flat version.** Use the engraved version only as a 6–8 frame flash, and drop the hatching.
4. **Fix the hybrid, or cut it by about 10:45.** Solid dots sized to the stroke (about 30 px pitch), no outline around the letter shape, and HOURS as a solid fill instead of a hairline.
5. Optional: merged outlines for the wire shot.

Don't spend more time on enamel or engraving polish, and don't add new identities.

## Where the ceiling is
- **Copy.** ETV gets variety from dozens of different names. You have one two-word phrase in four styles, so all variety has to come from fragmenting it into glyphs, rows and crops.
- **Silence.** The reference cadence is driven by music. A 2-frame strobe without sound can feel arbitrary or harsh, so screen that passage carefully.
- **Register.** The rendered enamel and engraving look will always read as a logo reel. The flat, misregistered and contour cards are where code can actually match the references.

## Decision

Accepted the editorial diagnosis, interleaving, removal of literal repeats, simpler dot construction and scratch removal. Rejected a 2-frame strobe passage because Olof requests controlled medium-high intensity and this cut is silent. A timing score or unique-frame count is not itself evidence of better rhythm.
