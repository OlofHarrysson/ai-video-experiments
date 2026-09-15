# The Matchbox Night Station — 12 seconds

A matchbox contains a railway station of impossible depth; its red matchheads become enormous suspended moons as we enter. Warm cardboard, pale splintered wood, scarlet sulfur and midnight-blue air give this shot a distinct domestic, industrial surrealism.

**Opening, 0s:** A half-open burnt-orange matchbox rests diagonally on a dark wooden table, its open drawer occupying the central half of the picture. Inside the drawer, two bright parallel rails run between rows of upright wooden matches toward a tiny amber-lit station canopy, slightly right of center. Scarlet matchheads hang above the tracks. The hollow sleeve frames the upper left; its torn cream edge and the exposed table establish household scale. The central route is wide and visibly empty, with deep blue night inside the box.

**Stage 1, 2s:** Close to the drawer's front lip, two rails cross a cream cardboard floor toward the same amber station canopy. Upright matches tower along either side, their square wooden stems catching warm light. The orange sleeve is cropped at the upper left, while the tabletop remains visible only in the lower corners. Red matchheads hang high above a clear central aisle filled with blue haze.

**Stage 2, 4.5s:** Inside a cavernous railway station built from a matchbox. Pale matchwood columns rise from long cardboard platforms beside the two rails. Their scarlet heads have swollen into round, rough-surfaced globes supported by narrow stems. The orange sleeve forms a distant overhead vault; torn paper fibers line its edges. The amber canopy remains ahead, visible through a broad opening between the columns.

**Stage 3, 7s:** Beside the near end of the amber canopy, long cream platforms extend into midnight-blue space. The matchwood columns stand at the outer edges; three enormous red globes hover above their shortened stems, with visible dark gaps underneath. The orange ceiling survives as one curled cardboard ribbon across the upper left, exposing a star-filled sky. Two luminous rails continue through the open center beneath the canopy.

**Stage 4, 9.5s:** An empty railway platform hangs in an immense midnight sky beneath three widely separated scarlet moons with granular sulfur surfaces. Pale splintered timber supports the amber station canopy at the right. Two rails converge toward a small warm light in the open distance. A curled orange cardboard edge remains at the far upper left, and cream paper fibers fringe the near platform, preserving the impossible matchbox world.

Append to every description: *Tactile surreal oil painting, crisp sculptural forms, deep atmospheric perspective, warm amber illumination against midnight blue, scarlet accents, broad readable shapes, spacious asymmetrical composition.*

**Destination and bounded motion:** Follow the visible rails toward the amber canopy, then settle beside it looking along the platform. Use existing eased Lanczos phrases, with normalized image coordinates and image-displacement travel signs as in M2/M4/M6. Suggested starting values below; align the pivots to the actual opening's clear aisle before execution.

| Time | Center / radius | Zoom amount | Turn | Travel x/y |
| --- | --- | --- | --- | --- |
| 0–3s | (0.60, 0.52) / 0.70 | 0.55 | +35° | −0.05, +0.01 |
| 2.7–6s | (0.80, 0.38) / 0.70 | 0.50 | −45° | +0.03, −0.025 |
| 5.7–9s | (0.60, 0.50) / 0.72 | 0.30 | +25° | −0.04, +0.02 |
| 8.7–11s | (0.50, 0.50) / 0.72 | 0.10 | −10° | 0, 0 |

About 3.32× cumulative scale; no further motion after 11s. Alternating local twists carry the sleeve aside and bend the match columns without an indefinite spiral. These are prescribed warps, not a promise of physical camera travel.

**Fixed recipe:** Recurrent Krea, previous warped painting as input, CFG1, three Euler intervals, 0.5s paints at 24 fps (cadence 12). Opening plus 23 repaints, last at 11.5s; 288 delivery frames with existing RIFE finishing. Preserve the accepted diffusion defaults.

**Failure signs to inspect:** Opening reads as an ordinary box with no visible interior destination; lip/sleeve swells across the rails instead of leaving frame; canopy repeatedly relocates; station appears in one abrupt repaint; red moons remain mushroom-like matchheads or become balloons; twists knot the rails or expose reflected borders. Inspect raw paintings around 4.5–8s for actual structural progression, and RIFE midpoints for doubled columns, translucent globes and smeared rails. Success needs both readable travel into the box and a clear change of scale, with the final platform retaining space to breathe.
