# Graphic-design quality test v003

2026-10-09. Olof identifies plain graphic design as the primary risk, authorizes experiments and offers Claude as a second pair of eyes. Three tightly composed original identities test visual craft before more effects are added. Theme remains undecided; sample words are design material.

## Intent

- **Night Fever:** compound script, diagonally fitted words, dimensional lacquer/chrome edges and ornaments attached to letter strokes. Reference family: script credit at 1:52.070. Avoid a solitary centered word with a disconnected underline.
- **Overload:** custom engineered two-line letters with notched counters and a continuous red/chrome construction. Reference family: rounded beveled letterforms at 1:55.490. Letter shapes and joins carry the detail.
- **All at Once:** oversized slab/block typography, smaller contrasting text and a dense interference field. Reference families: circular lettering at 1:51.236 and later editorial overlap at 2:06.960. Distinct palette and silhouette from the other two.

Stills were inspected at 1280×544 before rendering short stepped transformations and hard cuts. Earlier passes are preserved. Output remains a study, not a final logo, theme or finished film.

## Review artifacts

- [Three stills](output/design-board.png): [Night Fever](output/01.png), [Overload](output/02.png), [All at Once](output/03.png).
- [Nine-second silent motion test](output/motion-test.mp4), three seconds per treatment. Six held states per treatment, with hard reframing, two-line offsets and color changes. This tests abrupt motion vocabulary; it is not an escalating film edit.
- [Reference comparisons](../../references/inspection/design-v003/output/): original-reference pixels stay ignored. The script and chrome treatments use the reference's material and composition families; the red poster intentionally diverges in palette, background and layout.
- [Motion states](output/motion-states.png), [encoded transition inspection](output/encoded-review/v001/contact-sheet.jpg), and `output/report.json`.

## What changed and what remains

The script uses two large interlocking words, a descending diagonal, custom curves joined to the letter strokes, broad cream/pink edges and gradient fill. The engineered design fills most of the frame with seven original glyph shapes, nested counter edges and material bands; its primary strokes and counters are designed as paths. The poster pairs hollow-circle slab lettering with solid slab mass and diagonal script, using a red ground instead of another floating word on black.

Assistant assessment: Night Fever is a clearer improvement over the isolated Overdrive script. Overload now has an individual letter construction and material treatment, although it is more regular and logo-like than its reference. All at Once provides a distinct editorial identity, but the competing script and italic text make its hierarchy the least resolved. These are candidate directions, not human-approved designs or proof that the reference's full visual range has been matched.

The first pass was too flat in the gradients and included floating diagonal marks on Overload. Those marks were replaced with channels following the actual glyph contours. Subsequent passes strengthened the poster's circle texture and corrected bold/italic font syntax. All three earlier passes remain under ignored `output-*-pass/` directories.

## Implementation and validation

No new dependencies: Canvas 2D draws and composites cached design plates. This study uses explicit frame-indexed states rather than continuous GSAP tweens; GSAP remains available in the project for sequenced interpolation. Five local Mac faces are used and checked: Snell Roundhand, Rockwell, Didot, Helvetica Neue and Impact. Their font files are not bundled; cross-platform browser rendering is unverified. Overload's glyph geometry is original and only covers the letters in OVERLOAD.

All three pass same-time PNG hash comparisons after out-of-order seeking. The local preview's Play/Stop buttons were exercised. The assistant inspected all three full-size stills, the three reference comparisons and the motion-state sheet; the encoded MP4 was sampled frame by frame around the first scale change and the first identity cut. Full-speed perceived rhythm remains for Olof to judge. Export is 1280×544, 24 fps, 216 frames, 9 seconds, without audio.

From the project directory:

```sh
node studies/design-v003/render.mjs --motion
```

The renderer refuses to overwrite output. Preserve `output/` by renaming it, or set `DESIGN_OUTPUT=output-<new-version>`. Source-derived comparison sheets go under `references/inspection/design-v003/<output-name>/`. No reference pixels are embedded in the original artwork.

## Consultation

Claude CLI 2.1.280 was checked against current model documentation. The read-only `opus` / high-effort call failed before a model answered: `Failed to authenticate: OAuth session expired and could not be refreshed`. `claude auth status` reports logged out. No model identity or critique was returned; no advice is attributed to Claude. The prompt is saved in `consultation-prompt.txt`, and the failure receipt is local under `references/consultations/`. Restore the existing login with `claude auth login` to retry. No API-billed fallback was used.
