# The Malachite Run

**One twelve-second continuous rush: an underground malachite passage → a luminous violet jungle → an open vermilion canyon.** A silver stream leads through successive openings. Near arches, leaves and rock shoulders grow large and pass beyond the frame; a farther opening takes over as the destination. The intended pleasure is plunging through an extravagant living landscape, with a pronounced sideways weave and a travelling bend through the canopy.

Planning only, 2026-09-14. These are authored prompts and proposed motion values, not rendered results or guaranteed generation. The main agent owns selection, runtime, noise scheduling and implementation within the active motion hour.

## Composition and execution

The visual spine is a low viewpoint over a silver stream, converging near **x=0.52W, y=0.46H**. Keep a generous clear passage through the middle. Large cropped foreground forms, smaller middle-distance forms and a small illuminated opening establish three depth layers. Only the destination stays near the middle: the nearest frame must leave the view. The final canyon has open sky and separated cliffs, releasing the overhead enclosure.

Use the agreed recurrent Krea Turbo recipe: encode the warped previous painting, CFG1, three partial Euler intervals, changing seeds, two paintings/sec, 24 fps and existing RIFE finishing. Twelve seconds gives **288 delivery frames, 24 paintings at 0–11.5s, and 23 feedback repaints** after a newly generated opening. Motion finishes at 11.5s; the last half-second holds the final painting. RIFE remains outside recurrence.

Each full positive prompt is **one timed paragraph below followed by the fixed style paragraph**. Replace the event paragraph at each timestamp; hold it until the next event. These describe the visible scene at that instant. Explicit camera motion belongs to the warp schedule. Freeze the authored text without automatic prompt expansion. Prompt changes do not restart the noise schedule.

**Fixed style paragraph**

> An intricate surreal landscape painting with the tactile depth of carved minerals and translucent botanical specimens. Peacock green, electric violet and vermilion surfaces catch sharp silver highlights and warm saffron light, with deep blue-black recesses. Broad sculptural shapes carry delicate mineral bands, leaf veins and weathered edges. Strong foreground-to-distance scale differences, crisp surfaces, luminous atmospheric depth and a wide cinematic composition.

## Opening plus seven subsequent descriptions

### 0.0s / frame 0 — The mineral throat

> Just above a narrow mirror-silver stream inside an immense underground passage carved from banded malachite. A massive scalloped arch fills the near left and upper edges, its polished emerald ridges resembling the overlapping plates of a fossil. A broken arch foot occupies the lower right. Beyond it, two smaller irregular arches recede toward a bright slit slightly right of center. The stream is broad at the bottom edge and narrows between deep green banks toward that distant light. Through the slit, a few enormous violet leaves glow against saffron mist. Silver seams trace the stone's peacock-green whorls; reflected water light illuminates the underside of the nearest arch. The central passage is wide, luminous and unobstructed, with monumental dark forms close on either side.

### 1.5s / frame 36 — At the first threshold

> At the mouth of a malachite passage, huge cropped green arch shoulders occupy the extreme left and right edges and the upper rim extends beyond the view. The silver stream leads into a jungle of violet foliage visible across the broad central opening. Thick emerald roots clasp the nearest stone, with purple leaf blades sprouting between its mineral plates. Farther ahead, two leaning trunks form a smaller pointed opening over the water. Saffron light penetrates the leaf canopy, separating the close dark stone from the luminous vegetation beyond.

### 3.0s / frame 72 — Inside the violet jungle

> At stream level within a towering violet jungle. An enormous glossy purple leaf is cropped across the upper left, and a ridged emerald trunk stands close along the right edge. The silver stream bends gently right between thick exposed roots. Farther ahead, two smaller trunks lean together into a pointed arch slightly right of center, with bright yellow mist visible between them. Broad translucent violet leaves form overlapping fans at several distances. Emerald root ridges carry mineral-like bands, and silver droplets shine along the thick leaf veins. Vegetation fills the surroundings from the waterline to the high canopy.

### 4.5s / frame 108 — Under the living vault

> Deep within a violet jungle, the undersides of two immense ribbed leaves sweep across the upper corners, their thick stems cropped by the side edges. A close root curls out of view at the lower left. The silver stream widens across the foreground and narrows toward a small sunlit gap between distant trunks. Beyond that gap, vermilion rock faces and a strip of saffron sky are visible. Purple leaf veins glow like stained glass above dark emerald roots; patches of orange mineral crust cover the roots nearest the distant opening. Clear water and open space occupy the middle of the view.

### 6.0s / frame 144 — The forest opens into stone

> A broad silver stream crosses the boundary between a violet jungle and a vermilion rock gorge. Huge purple leaves and green roots remain close along the left edge, while a sunlit red cliff shoulder rises close on the right. At the upper corners, thick leaf ribs have hard orange mineral edges. The opening between the foliage and the cliff reveals a spacious canyon beneath saffron sky. Two separate red buttresses stand farther along the stream, their curved inner faces framing a small luminous gap. Long silver reflections connect the shaded foreground water to the bright canyon beyond.

### 7.5s / frame 180 — Through the canyon gate

> At the sunlit entrance to a vast vermilion canyon. A massive curved red cliff is cropped close on the left; a dark glassy rock shoulder fills the near right edge. A few violet leaf tips hang at the extreme upper left. Open saffron sky spans the upper middle between the separate cliffs. The silver stream runs between their broad bases and curves left toward smaller red formations in the distance. Layered orange stone carries sweeping emerald mineral veins, and polished obsidian seams catch narrow white reflections. Deep shadows at the cliff feet contrast with the bright open land ahead.

### 9.0s / frame 216 — Between the red giants

> Low over a silver stream inside an open vermilion canyon. Two enormous separated rock buttresses occupy the outer edges, their nearest surfaces heavily cropped. Beyond them, a broad ochre basin opens beneath a saffron sky, with three slender curved red monoliths diminishing toward the horizon. The stream makes a long bright S through the basin. Emerald mineral bands wrap the near cliffs, and black glass seams divide their sunlit orange faces. A low pale sun shines through the distant gap; long shadows across the canyon floor reveal the distance between each formation.

### 10.5s / frame 252 — Release into the basin

> Above a widening mirror-silver river in an immense open ochre basin. Large vermilion cliff shoulders are cropped at the far left and right, with uninterrupted saffron sky above the central landscape. Three tall curved red monoliths stand widely separated in the middle distance, their black glass seams and thin emerald bands catching the low sun. The river bends between them toward a pale luminous horizon. Broad empty stretches of sunlit mineral ground surround the monoliths; distant red ridges are softened by golden haze. The foreground water carries long bright reflections beneath the dark edges of the nearest cliffs.

## Motion recipe for the main agent

**Keep forward magnification active across both environment changes.** The table specifies total changes per eased phrase, not per frame or repaint. Overlap phrases so one accelerates while the preceding one decelerates. Use the existing bounded composition and Lanczos remapping. All four similarity phrases share the destination center **(0.52W, 0.46H)**; localized twist radius is **0.75H**. Positive travel means screen content moves right/down.

| Time | Total scale | Local twist | Content travel x/W, y/H | Intended reading |
| --- | --- | --- | --- | --- |
| 0.0–3.3s | 1.50 | +12° | −0.055, +0.010 | Rush into the first opening; the near mineral arch grows beyond the edges. |
| 2.8–6.3s | 1.48 | −18° | +0.095, −0.015 | Weave through the jungle; close leaves sweep sideways while the next gap approaches. |
| 5.8–9.4s | 1.45 | +12° | −0.065, +0.010 | Push through the forest boundary and between the canyon shoulders. |
| 8.9–11.5s | 1.35 | −6° | +0.025, 0.000 | Continue outward into the basin, then ease to the short final hold. |

These scales multiply to approximately **4.35× cumulative magnification** before repainting, making this a deliberately strong motion proposal. It requires regenerated scene content: simply enlarging the opening cannot reveal those spaces. The final landscape becomes more open through its scene description and the departure of near forms, while zoom stays positive.

Add **one horizontal travelling shear wave** after the four similarity phrases in mapping order: `start=2.5`, `duration=6.0`, `amplitude=0.07`, `wavelength=1.10`, `cycles=1.0`, `phase=0`. Amplitude and wavelength are in image-height units; the existing envelope returns the wave displacement to zero at 2.5s and 8.5s. Intended effect: a broad travelling bend through the jungle's leaves and roots, strongest around the living-vault/boundary stages. It affects the full image, including the stream; it is not a foliage mask. End it before the open-basin finish so the final forward glide reads clearly.

Translate table scales to `zoom=scale−1`. The current transform uses image-height coordinates: center becomes `[0.52*W/H, 0.46]`, and horizontal travel becomes the listed x/W value multiplied by W/H. Vertical travel, wave values and radius already use H. These are proposed starting values for a motion-only preview, not validated amplitudes.

## What makes this shot succeed

Screen the opening for three distinct depth layers and a clear route through the center. In the motion preview, watch the first arch enlarge decisively and leave the frame, while the destination remains navigable. If the wave obscures that route, reduce its amplitude first; preserve the forward scale schedule as the shot's main action.

At approximately **0.5s, 4.0s and 9.5s**, the raw paintings should read independently as mineral passage, living jungle and open canyon. Across the sequence, near silhouettes should leave the frame and smaller farther silhouettes should take their place. A fixed central arch that changes surface color fails the travel intent. Repeatedly redrawing a small opening at the same scale can also undo the approach; the progressively cropped foreground descriptions are intended to discourage that, without guaranteeing it.

Inspect raw paintings at the jungle entrance and canyon threshold before RIFE playback. The remaining risks are abrupt semantic replacement, accumulated detail loss under strong magnification, displaced or reflected borders, and doubled leaf/cliff edges during interpolation. Apparent forward travel is a creative illusion assembled from 2D warps and recurrent repainting; no depth reconstruction or actual camera translation is claimed. The planned continuous rush and gradual environment changes remain unproven until rendered and reviewed.

Design basis: the active [motion-hour brief](README.md), the previous [creative plan](../two-hour-lab/creative-plan.md), and the saved [Krea feedback prompting guidance](../../../../../../docs/research/prompting-for-feedback.md). This handoff contains one shot; runtime and all implementation remain with the main agent.
