# Rainbow Mane: creative brief

Olof's direction, 2026-09-30: an eventual 30–60 second short with a purpose, plot or event. Pretty imagery alone is insufficient. Begin with a close-up of a cartoon character with a round white face and rainbow mohawk. The character turns sideways; the mohawk becomes a horse's mane and the face becomes a horse's head. Pull back to reveal the white horse, retaining the rainbow crest. The ending is deliberately unresolved. This first test establishes what the existing workflow can do.

## Visual direction

Four user-supplied screenshots from the second Spider-Verse film are preserved in `references/assets/`, with hashes and source notes in the reference manifest. User timecodes: 01:08:15, 01:08:31 and 01:08:29. No direct inspection of the film file or verified timecode-to-image mapping has occurred.

Observed visual features: saturated magenta/pink and acid yellow; cyan and violet accents; strong black shapes and unruly ink strokes; visible halftone dots; layered printed textures and slightly offset color edges; dramatic diagonals and strong subject/background separation. Use these as visual vocabulary for an original character. The white face/body and rainbow crest must remain readable against the busy world. No film characters, logos, subtitles or copied scene composition are requested.

## First passage

1. Establish a round white face, clear eyes and one rainbow mohawk.
2. Change from front/three-quarter to a right-facing profile while keeping the crest readable.
3. Elongate the muzzle, develop equine ears and neck, and carry the same rainbow into a mane.
4. Pull back from the horse head to a white horse body.

Provisional assistant target: approximately 8–12 seconds for this feasibility passage. Screen the opening before recurrence; inspect the turn before extending; preserve failed attempts and branch from the last useful painting. Do not stretch a failed turn into a finished 30–60 second film.

The eventual story needs motivation and a payoff. The initial transformation is an event, not yet a complete plot. Choose what the horse wants or does after the first passage is reviewed; no ending has been approved.

## Method and uncertainty

Retain the current recurrent Krea loop: previous painting → spatial warp → partial-noise initialization → text-conditioned repaint → next painting. The screenshots inform descriptive prompts, not additional image conditioning. Generate the opening with Krea too. Use the existing three-interval Euler/CFG 1 repaint recipe and recorded independent seeds. Preview camera motion separately; a flat-image warp does not establish a character's 3D head turn. RIFE is finishing only and never feeds back into generation.

Main unknown: whether a staged description produces a readable turn and connected human-to-horse morph while retaining the white/rainbow identity. Multiple faces, abrupt replacement, disappearing eyes, loss of the crest and missing body anatomy count against success. Olof decides the style and playback quality after assistant screening.

## Current experiment — 2026-10-01

After the first passage, Olof says the style is pretty good but the transformations are too abrupt. He first requests a character already in profile and a simple authored animation of the face becoming a horse, with the camera fixed. He approves the [four-second motion plan](experiments/profile-morph.md) and authorizes [guided Krea repainting](experiments/guided-repaint.md). The two painted tests show more connected shape progression, with contour artifacts and reduced visual richness still unresolved. The supplied comic-print direction remains the target; the drawing's flat treatment has not replaced it. The head turn, full-body reveal and story ending remain unresolved.

Olof then calls the guided result "pretty good" and says it restyles the input well. He wants the drawing to serve as a graybox and approves a [separate experiment](experiments/graybox-video.md) using the same four-second motion, a neutral shape/depth guide, and one finished appearance reference in a video model with structural guidance. Whole-clip generation is authorized for this comparison; the existing Krea feedback result remains the baseline. This does not approve the sketch's flat appearance as the finished style.
