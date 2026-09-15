# Fluent and varied spatial movement

2026-09-15. Olof likes the story-hour films and asks for another hour: keep large spatial changes while reducing repeated pauses, repetitive zooms and jerky motion. Combine pans, rotation, zoom-in/out and regional warps. His feedback supports the creative direction; preference among this session's films is pending.

The motion paths now overlap: a turn can continue while forward travel eases into a pullback, and a regional twist can continue through the next directional change. This removes the old internal full stops in the matched paths. It does not remove abrupt diffusion redraws or guarantee constant screen speed. The stronger arc is the assistant's preferred matched candidate; the gentler pair alone would have traded away too much movement.

## Shortlist

- **[The orbital railway — 21⅓ seconds](../../exports/fluent-hour-v001/f6-the-orbital-railway/assembled/preview.mp4):** fruit-city → fish → garden → railway → floating water-world. Continuous movement starts at the opening; the final passage pulls back and rolls instead of pushing forward again. Assistant first choice for this motion brief.
- **[The dreaming moon — 29⅓ seconds](../../exports/fluent-hour-v001/f5-the-dreaming-moon/assembled/preview.mp4):** the preserved fruit/garden opening continues into a railway, a library beside a face, moon faces and sailing ships. The new overlapping path begins at 10⅔ seconds. Assistant alternative for its unexpected imagery.
- **[Bolder arc — new 10⅔-second passage](../../exports/fluent-hour-v001/f4-bolder-arc/excerpt-0384/rife-moving-tail/preview.mp4):** the clearest matched test of greater movement without the earlier internal stops.

The [reviewer](http://localhost:3028/) compares the gentler and stronger arcs from the same starting frame, at equal duration. [New ending excerpts](http://localhost:3028/fluent-endings) show the moon and water-world alternatives; these have different starting scenes and lengths. Complete films are linked above and surfaced in chat.

## Comparisons

| Attempt | What changes | Assistant observation |
| --- | --- | --- |
| F0 Previous movement | Reuse the previous garden-to-library paintings | Historical control; no new inference. Separate motion phrases have repeated stops. |
| F1 Arcing route | Overlapping roll, pan, inward/outward zoom and local turn | Readable railway and a surprising face/library ending; gentler than the old route. |
| F2 Woven route | Longer lateral drift and overlapping local twists | A clear curving railway, but a near staircase occupies much of the view and overall movement is weaker. |
| F3 Sweeping worlds | Regenerate from the same fruit opening with continuous overlapping movement | The fruit-city, fish, garden and railway remain readable while their framing changes. A strong whole-shot candidate. |
| F4 Bolder arc | F1 motion magnitudes ×1.6; all other controls identical | Stronger push/pull and turns, with a dark profile emerging beside books and musical ribbons. Some interpolation ghosting remains. |
| F5 The dreaming moon | Continue F1's actual face/library result | Faces with windows turn into moon faces and sailing ships. The requested crescent is not literal, but the material links are readable. |
| F6 The orbital railway | Continue F3's railway with a sustained pullback | A floating water-world emerges between railway arcs. The pullback opens the composition; the requested split globe remains unrealized. |

[Earlier versus connected movement](http://localhost:3028/fluent-control), [gentler versus stronger](http://localhost:3028/fluent-strength), [two gentler routes](http://localhost:3028/fluent-paths), [regenerated opening](http://localhost:3028/fluent-worlds). These pages use the same 24 fps presentation. The matched excerpts start at original source time 16s; no inference is claimed for their omitted shared prefix.

## What stays fixed

Recurrent Krea Turbo: encode the warped preceding painting, add independent noise, run three Euler intervals with CFG1 and the recorded scene-specific noise/prompt schedules. Lanczos spatial transforms precede each repaint. New source paintings occur every half-second at 24 source fps. Finishing preserves every painting and presents the sequence at 1.5× speed: three paintings per displayed second, eight output frames between painting timestamps, 24 fps. RIFE 4.25 scale 1 fills intermediate frames and never feeds back.

F1/F2/F4 have identical prompts, noise, seeds, timings and shared prefix through frame 384. F3 uses the same opening image and the prior journey's prompts, noise and seeds through source time 24s. Their control equality and each recurrent parent/input are checked from actual files. F5/F6 are creative continuations, not single-variable comparisons.

## Review and findings

The [independent review](motion-continuity-review.md) separates geometry from generated-art evidence. F4 has median prescribed movement 94.1 px/source-second, close to the previous 94.6, without the old interior full stops. Its net contraction is 26.52%; F1 is 15.51% and F2 only 3.91%. These are geometric measurements, not perceptual smoothness scores. Reflected boundaries and redraws can still interrupt the visual result. The shared historical opening also retains its earlier movement; only F3 restarts that opening with the new path.

Main review uses evenly sampled paintings, complete diffusion provenance, short interpolation screens, and denser frame selections around conversions and direction reversals. The fruit-to-building conversion in F3 still shows ghosted towers/seed shapes in intermediate frames around delivery 108–116. F4's first reversal carries spatial movement through the turn, but its train changes design. Independent late-frame review of F1 finds readable face/moon forms with mild detail softening and a tightly cropped face. Frame inspection is not a human playback judgment.

The inherited faster finishing helper held seven frames after the last painting. That caused an unintended ending stop on paths still in motion. [moving_tail.py](moving_tail.py) preserves every frame through the final painting, then generates the remaining seven frames from its actual time-based warp. Exact pixel checks verify all seven and their differences. The reviewer labels them “Spatial warp.” Historical finishes remain preserved. This correction leaves RIFE between paintings unchanged.

## Execution

Use `uv run --locked python projects/modern-model-study/experiments/fluent-hour/run.py` from `apps/deforum`; the runner reuses the audited two-hour implementation. [Configs](configs/) freeze the tested paths. [preview.py](preview.py) shows motion before diffusion; [retime.py](retime.py) produces the existing pair-gated RIFE finish; [moving_tail.py](moving_tail.py) corrects its new-film ending; [assemble.py](assemble.py) joins verified adjacent prefixes without rerendering them.

Started 13:51 UTC, with new experiments allowed until 14:51 UTC. The prior conservative cumulative budget was $3.30 of $10. Final accounting, archive verification and cleanup are recorded at completion below.

## Completion and practical lessons

Six new recurrent attempts use **180 image jobs** on one temporary RTX PRO 4500. All 3,184 archive entries, recurrent parent/warped inputs, nine final deliveries and both complete-film assemblies are verified locally. The assemblies preserve every painting and the exact already-finished prefixes. [Execution summary](execution-summary.json) records the artifact hashes, counts and cleanup.

The owned Pod was deleted by 14:38:17 UTC after all generated artifacts were downloaded and checked; 360 remote media files and owned scratch were removed. The cleanup command completed with exit code zero. The retained 50 GB `deforum-models` volume remains. The final account check shows $0.5467354 posted debit and $0.005/hour retained storage; billing can lag. Reserve **$0.65** for the session, **$3.95/$10 cumulative**. No compute remains running.

The local disk approached capacity during archiving. Identical media was linked by verified hashes, and redundant earlier archive containers were retired only after a complete equal-file superset was local. No unique generation was discarded. The complete archive and canonical exports remain on disk.

**What to reuse:** overlap broad motion phrases; keep some pan/roll active through a change in zoom direction; use a deliberate pullback to reveal a larger surrounding world; adapt the next prompt to visible forms. Keep F4 as a stronger motion candidate, not a new unreviewed global default. F1/F2 show that removing pauses by weakening motion can miss the brief.

**What remains unresolved:** RIFE ghosts at larger redraws, reflection-created edge motifs, crowded near objects and some late flattening. The F6 water-world reveal still ghosts at excerpt frame 36. F5 has a readable changing face in dense frames 64–92, with some blended cheek detail. Neither path tracking nor prompt text gives complete object control. A useful next step is to branch near a successful reveal and redirect the next movement around its actual silhouette, retaining these paintings as reviewable checkpoints.
