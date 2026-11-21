---
thread_id: import:codex:01a1c74b-013d-73e2-8add-1c6182206a1a
title: Reverse engineer Do It Big
provider: codex
model: gpt-6-astra
created: 2026-11-10T21:09:06.163Z
settled: 2026-11-10T23:20:44.557Z
link: "[Reverse engineer Do It Big](t3-thread://v2/071bdbdb-bba7-4e87-b692-3de2e92037b2/import:codex:01a1c74b-013d-73e2-8add-1c6182206a1a)"
---

## Outcome

Reverse-engineered shuvfx's "Do It Big" (a girl's unicorn drawing growing into
fantasy) as designed shot images animated with short image-to-video actions and
tight editing, then started an homage, "Sunlit Sketchbook". A ten-second silent
opening was made, Olof found it flat, and a richer source-guided room still was
produced and left for his look check.

## Decisions

- Method: make each shot's starting image first, then animate it with a motion
  prompt. The creator's tools are unconfirmed; this is a visual inference.
- Stills with Nano Banana 2.1 through the Fal plugin (not the direct API). Olof
  accepted the four keyframes; he would have preferred the galaxy setting to the
  forest, which matches the original's opening.
- After the first cut Olof asked for more camera motion, better storyboarding and
  more detail. Agreed storyboard: room push past foreground leaves, angled pencil
  insert, transformation, galaxy reveal.
- The room was remade using an original film frame for light, texture and depth,
  with only the girl's face and hair as a character reference (room-v003).

## Changes

`apps/deforum/projects/sunlit-sketchbook/`: 50f1fd1 (plan and prompts), 71088e2
(keyframes), 68107fc (ten-second opening), 56a6cb4 (source-guided room still).

## Open ends

- Olof's verdict on room-v003 ("does this address the flatness?"), then the other
  revised shots, animation and music.
