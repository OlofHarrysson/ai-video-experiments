# Spider-Verse dinner montage

A study of the dinner-table time-lapse in *Spider-Man: Across the Spider-Verse* (2023), and a plan to make our own version from AI-generated paintings. Olof chose the scene on 2026-09-27 and describes it as stop-motion.

**Status:** reference extracted and measured. The recreation approach awaits Olof's choice; see the [proposed first experiment](#proposed-first-experiment).

## The reference

From 3:57.6 to 4:02.8, Gwen sits at the head of her family's dinner table with her eyes closed while everyone holds hands for grace. Sixty-three paintings of that moment replace each other at twelve per second. Her pose and place in the frame stay fixed while everything else changes: hair, clothes, the people at the table, food and holidays, time of day and palette. The camera pulls back throughout, from her face to the whole table. Years of family dinners, with Peter Parker at many of them, pass in five seconds before the film cuts to Peter being bullied at school.

It reads as stop-motion because each image is held and then replaced, with nothing in between. The images themselves are painterly CG in Gwen's watercolor world, Earth-65; [how the Spider-Verse films were made](../../../../docs/research/spider-verse-making-of.md) covers that look and its sources.

### Measured timing

| Measure | Result |
| --- | --- |
| Position in the film | 3:57.571 to 4:02.784: 5.21 seconds, 125 frames at 23.976 fps |
| Images | 63: 62 held for two frames, the last for one |
| Rate | 12 new images per second, "on twos" |
| Image changes | Every swap changes a 16 px colour thumbnail by at least 14.75 (0–255); movement within an image stays below 6.3 |
| Within each image | No frame repeats exactly (mean detailed change 5.05). The picture moves on every frame, consistent with the camera pulling back on ones while images change on twos |

Frame-by-frame values are in [montage-cadence.json](references/montage-cadence.json), produced by [extract_reference.py](scripts/extract_reference.py).

### Structure

| Images | From | Framing |
| --- | --- | --- |
| 1–24 | 3:57.57 | Close-up: face and shoulders against a window, curtains and plant leaves |
| 25–32 | 3:59.57 | Medium: joined hands reach the frame edges; the table edge appears |
| 33–40 | 4:00.24 | Medium-wide: family members at her sides, plates, a birthday cake |
| 41–63 | 4:00.91 | Wide: the whole table, mostly evening blues, costumes and Christmas hats |

**Fixed:** Gwen centred with head bowed and eyes closed, a smooth framing path, the window behind her, curtains on both sides, leaves on the left, backlight from the window.

**Changes with every image:** hairstyle and colour (blonde bob, blue buns, pink streaks, beanies, braids, a top-knot), clothes and accessories, apparent age, who sits beside her, table dressing, the time of day outside, and the palette: pastel daylight, golden orange, violet and deep blue night.

### Why it works

Assistant reading, not tested:

- One locked anchor, her pose and position, makes the swaps read as time passing rather than as cuts.
- The steady pull-back gives the rapid changes a direction: the story widens from Gwen to the family around her.
- At twelve images per second the viewer registers change and mood rather than each picture.
- In Earth-65, colour follows Gwen's feelings, so the palette shifts carry emotion as well as time.

### What will be hard with AI

1. Locking pose and composition across 60 separately generated images.
2. Placing each image on a smooth framing path from close-up to wide.
3. Keeping one recognisable character while hair, clothes and age change.
4. The Earth-65 look: wet watercolor washes, vertical brush striations, a cyan, orange and violet palette.
5. Timing: images on twos, camera motion on ones, and no interpolation between images.

## Proposed first experiment

**Question:** do generated variations of one composition, swapped twelve times per second under a slow pull-back, read as time passing?

**Shortest useful test:**

1. Generate one base painting at the widest framing and high resolution: a character at the head of a dinner table, eyes closed, holding hands, window behind, watercolor style.
2. Derive 24 variations with an image-editing model, changing only hair, clothes, table dressing, time of day and palette.
3. Assemble two seconds: each image held for two frames under a digital pull-back that moves every frame. No RIFE.
4. Screen the clip, then show it to Olof beside the reference.

If the swaps read as time passing, extend to five seconds with a close, medium and wide framing path, generated per band or guided by a simple Blender blockout.

**Open decisions for Olof:**

- **Character:** a faithful Gwen study, or an original character in the same technique. This repository is public; the assistant recommends an original character.
- **Image model:** to be proposed from current options before any generation.
- **Scope:** the montage alone, or the whole dinner memory from 3:44 to 4:10.

## Files

- [References and provenance](references/README.md): film clips and stills stay local and ignored by Git.
- [Measured cadence](references/montage-cadence.json) and its [extraction script](scripts/extract_reference.py).
- [How the Spider-Verse films were made](../../../../docs/research/spider-verse-making-of.md): people, techniques, interviews and related films.
