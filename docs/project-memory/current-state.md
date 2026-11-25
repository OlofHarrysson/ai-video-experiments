# Current state

Updated: 2026-11-25

## TL;DR

- A public notebook of AI-assisted film experiments.
- Focus: Sunlit Sketchbook, the only project still in active image work.
- Watch out: the shelved Deforum films no longer have their source stills.

## Now

- Image-first video: design shot stills (Nano Banana via Fal), then animate them
  with short image-to-video actions. Being tested in Sunlit Sketchbook.
- Code-drawn Remotion films with a shared picture and sound timing grid:
  The Curve (Three.js, silent, locked) and The Moon Fisher (pixel-art engine,
  11-bone rig, sampled-instrument score).
- Hybrid typography: AI-generated images as finished artwork, code deriving masks
  to reveal and time them (Filmhack type reel).
- Deforum/Krea feedback films are shelved; their videos play, but their PNGs are
  deleted (`docs/storage.md`), and `docs/current-state.md` holds their handoff.
- Claude Code gets the repository skills via `.claude/skills` and the hosted
  RunPod MCP server via `.mcp.json`.

## In progress

No unsettled threads. Open work from settled threads:

- Sunlit Sketchbook: room-v003 look, then revised shots, animation, music.
- The Moon Fisher: sound effects (synthesized versus free recorded).
- The Curve: score on its 120 BPM sync points.
- Filmhack type reel: Olof to choose layered design, video model versus code, or audio.

## Recent decisions

- 2026-11-22: Deforum projects shelved; the last four films' PNGs (55 GB, including
  generated paintings) deleted to free disk, leaving Deforum at about 75 GB.
- 2026-11-10: Sunlit Sketchbook stills use original film frames for light and
  depth, with only the character's face as reference. [Thread](threads/2026-11-10-sunlit-sketchbook.md)
- 2026-10-17: The Curve v005 locked as the current cut ("it lands").
  [Thread](threads/2026-11-11-the-curve.md)
- 2026-10-12: For hybrid animation, plan separable parts before generating; motion
  is only as fine as the parts. [Thread](threads/2026-11-12-filmhack-type-reel.md)
- 2026-10-01: The Moon Fisher uses palette fades only where time passes and ends
  on the cat with its fish. [Thread](threads/2026-11-11-moon-fisher.md)

## Known problems

- Generated stills read flatter and more outlined than the references
  (Sunlit Sketchbook).
- Moon Fisher's cat pounce lacks a true crouch and its tail is stiff.
- Continuing any Deforum film means regenerating its input stills.

## Likely next steps

- Continue the Sunlit Sketchbook storyboard from the room-v003 still.
- Score The Curve; add sound effects to The Moon Fisher.
