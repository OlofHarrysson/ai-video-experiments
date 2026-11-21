---
thread_id: import:codex:01a0b157-a6be-7a63-a594-9d7dd7ddea22
title: Windy Puppy Digital
provider: codex
model: gpt-6-astra
created: 2026-09-17T21:49:09.840Z
settled: 2026-11-16T10:53:46.129Z
link: "[Windy Puppy Digital](t3-thread://v2/071bdbdb-bba7-4e87-b692-3de2e92037b2/import:codex:01a0b157-a6be-7a63-a594-9d7dd7ddea22)"
---

## Outcome

A personal side job, not a film experiment: turn a small online photo of a puppy
painting into a large wall print. After a blurry €3 test print, the painting was
repainted with OpenAI's Sunburst image model, upscaled once with Topaz and
exported as a 65 × 80 cm, 300 PPI canvas file (7677 × 9449 px). Nothing has
been ordered yet.

## Decisions

- Crop the frame exactly from the original pixels; the first generative frame
  removal subtly reinterpreted the painting. Edge shadow was cleaned only in a
  12 px border, with the centre verified pixel-identical.
- Topaz through the Fal API (key in a local `.env`) for upscaling. Two passes
  were only a workaround for the per-pass limit, not a quality recommendation.
- The 300 PPI test print looked blurry from 1 m, partly because the source photo
  was already soft. Olof chose to improve the artwork itself: several image-edit
  passes, then one maximum-quality Sunburst edit (about $0.30–0.50), which he
  preferred when zoomed in.
- Format: frameless canvas stretched on wood, coral-red printed sides, no
  passe-partout. Size moved from 60 × 75 to 65 × 80 cm (the shop sells 5 cm steps).
- On 2026-11-13 Olof agreed to crop the existing Sunburst image rather than
  regenerate with a newer model. One Topaz CGI upscale (about $0.16), top red
  strip cropped, local resize to 300 PPI.

## Changes

No repository changes. Files live in `~/Downloads/`, including
`dog-painting-canvas-65x80/send-to-print-shop/puppy-sunburst-65x80cm-300ppi.jpg`
and German printing instructions (`Druckhinweise.txt`).

## Open ends

- Choose the canvas (Sihl Lisa 390 g or Canson PhotoArt ProCanvas 395 g; the
  shop's standard Canvas Artist is a third option) and get all-inclusive quotes
  for 65 × 80 cm with red sides. Lisa estimate about €80–96; Canson price unclear.

## Working preferences

- Use the built-in browser to read web pages rather than Python scraping scripts.
- When options involve sizes or crops, show them visually (an HTML comparison,
  wall mock-ups) instead of explaining in text. Olof flagged repeated
  misunderstandings over the frame shortlist.
- Prefer exact crops of the original over generative edits where fidelity matters.
