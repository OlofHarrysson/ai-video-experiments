# Handoff: plan the next Remotion film

Paste the prompt below into a new chat started in `/Users/olof/git/ai-video-experiments`. Rename this folder once the film has a title.

---

You are the director and production lead for a new short animated film in this repository, built with Remotion. Olof sets artistic direction and judges taste; you research, propose, build and screen. This chat is for **planning**: concept, style, storyboard and a rough animatic. Final production comes later.

## Read first

- `AGENTS.md`, then `apps/remotion/README.md`.
- `apps/remotion/projects/filmhack-frenzy/README.md`: the previous Remotion film. Reuse its mechanics: a shared timing grid for picture and sound, Studio compositions per scene, ffmpeg muxing for exact audio sync, and screening by contact sheets.
- `docs/olof-learning-journal.md` (the Filmhack entries) and `docs/review-and-feedback.md`.

## What Olof wants

- **Calmer than the Filmhack frenzy cut.** Not chaotic. Story and rhythm matter more than density of effects.
- **A pixel-art or simplified animation style**, mostly drawn in code. Code-drawn components, SVG and raster images are all fine, and they can be mixed; perhaps a background image. No video clips.
- **High-quality assets are the main craft goal.** Plan with simplified assets first, make a rough cut, then return to individual assets and improve them where they don't look good.
- **The subject is undecided.** Finding it is the first job.

## Plan of work

Agree on each step with Olof before building the next; keep feedback loops short and visual.

1. **Concept.** Ask about purpose, audience, platform and length only as far as needed. Propose 3–5 distinct premises, each with a one-line logline, a story arc (setup, turn, payoff) and why it suits pixel art and code. Help Olof choose or combine.
2. **Brief.** Record the chosen premise, length, aspect ratio, tone, audience and what the ending should make the viewer feel.
3. **Style frame.** Before the storyboard, fix:
   - the logical resolution and pixel scale (for example 270×480 scaled 4× to 1080×1920)
   - a limited palette
   - how outlines, shading and dithering are drawn
   - frame rate and animation cadence (for example new poses every second or third frame)

   Then build one finished-looking still in Remotion and screen it with Olof. Keep more than one stylistic option if the choice is close.
4. **Storyboard.** Scene by scene: beats, timing, camera, what moves, sound. Render one panel per shot from Remotion using placeholder assets, and present them as a contact sheet.
5. **Asset plan.** Keep a register listing each asset, its type (canvas function, SVG component, sprite sheet, raster), the shots that use it, and its status (placeholder, rough or final). Give every asset a fixed interface (for example `<Hero pose="wave" facing="left" />`), so a placeholder can be replaced by a better version without touching scenes.
6. **Sound direction.** Decide early, because timing drives the cut: licensed or found music chosen first and cut to, or a synthesized score on the film's beat grid. Olof found the last synthesized score annoying and unmelodic, so treat melody and restraint as requirements.
7. **Animatic.** Assemble the rough cut from placeholders at final timing, with temp sound. Olof reviews story and rhythm here, before asset polish.
8. **Upgrade passes** (the next phase, not this chat). Improve assets one at a time, highest-visibility first, re-rendering affected shots and comparing them before and after.

## Technical notes

- Pixel art in Remotion:
  - Draw into a low-resolution `<canvas>` from `useCurrentFrame()` and scale it up with `image-rendering: pixelated`, or use SVG with `shape-rendering: crispEdges`.
  - Snap positions to the pixel grid.
  - Sprites can be arrays of palette indices in code or PNG sprite sheets.
- Keep rendering deterministic: Remotion's `random(seed)`, never `Math.random()`.
- Start a new project folder under `apps/remotion/projects/`. Keep its own dependencies, a README brief and versioned renders, following the repository's workflow and storage docs.
- Run Studio through Devrun, per the shared terminal hub skill, when Olof wants to preview.

## Deliverables of the planning chat

- The brief.
- The approved style frame.
- The storyboard contact sheet.
- The asset register.
- The sound decision.
- An animatic render.

Record all of them in the project README.
