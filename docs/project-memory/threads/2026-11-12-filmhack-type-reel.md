---
thread_id: import:claudeAgent:cd1e87ff-9490-4477-a4aa-6b6a74e74c62
also_thread_ids:
  - import:claudeAgent:920b0edb-b5b0-4fcb-92d3-ce7b46ee1aba
title: Typography-driven Filmhack video
provider: claudeAgent
model: claude-opus-5-5
created: 2026-10-10T06:50:21.063Z
settled: 2026-11-12T20:28:45.111Z
link: "[Typography-driven Filmhack video](t3-thread://v2/071bdbdb-bba7-4e87-b692-3de2e92037b2/import:claudeAgent:cd1e87ff-9490-4477-a4aa-6b6a74e74c62)"
---

## Outcome

A 9:16 Instagram Reel concept for Filmhack (a free 48-hour AI film event in
Babelsberg, aimed at hesitant classic filmmakers), using the "doubt vs answer"
direction: a filmmaker's doubt types on and a big typographic answer shouts back
on the beat. It reached a 6-second motion proof where AI-generated images are the
finished artwork and code only animates them. Olof judged the result weak as a
film and moved the goal to learning; the thread ended on a comparison of ways to
split a generated image into animatable parts. The earlier thread `920b0edb` is
the same opening prompt, interrupted after one message.

## Decisions

- Reference study of Enter the Void (01:50–02:10) and All Of The Lights shaped
  the idea: one name passing through many identities, and music deciding when
  type gets huge. 140 BPM timing.
- Image generation through OpenRouter's images endpoint, budget up to $10
  (about $2.03 used).
- "Hybrid" cards beat code-drawn ones: Olof preferred the chrome YES, where the
  generated PNG is the artwork and code derives masks from its pixels to reveal,
  light and time it. The marquee and CREWS cards were converted to the same method.
- Olof's verdict (2026-10-10): the picture isn't beautiful enough, the sound is
  poor and the message unclear; the type-heavy style was probably the wrong
  choice. Continue anyway to learn as much as possible.
- Finding: motion can only be as fine as the parts. Generating parts separately
  (transparent background, gaps between letters) gives the cleanest pieces at the
  cost of the design; SAM 2.1 segmentation rescues an existing image but needs cleanup.

## Changes

`apps/canvas-animation/projects/filmhack-type-reel/`: commits 5813e60 (reference
study, script, keyframe targets), f1b4e44 (motion proof v001), 660772c (hybrid
marquee and CREWS), d1dc5bc (layer breakdown sheets, Olof's review), 34398d6
(three part-splitting methods compared).

## Open ends

- Olof was asked to pick the next step: a layered generated design, image-to-video
  model versus code animation, or audio. No answer in the transcript.
