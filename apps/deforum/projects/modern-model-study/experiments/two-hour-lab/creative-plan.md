# Two changing worlds — creative proposals

Planning only, 2026-09-14. **Recommend Velvet Flood first; Porcelain Weather is the brighter, more graphic alternative.** Each is a fourteen-second continuous recurrent shot with three different environments. These are unrendered hypotheses. The main agent chooses the sequence and sampling recipe within the existing two-hour session: no new experiments after 17:43:47 UTC today, maximum $10 incremental session spend.

## Shared execution shape

- Generate a new opening with **Krea 2 Turbo**, then initialize every subsequent repaint from the warped previous generated painting. Keep the same model throughout each film.
- **14 seconds, 24 fps, 336 delivery frames.** Start with two paintings/s: anchors at 0, 0.5, …, 13.5 seconds; 28 paintings including the opening, hence 27 feedback repaints. Uniform four/s would require 56 paintings including the opening. More paintings do not by themselves establish a gradual structural change.
- Use the existing RIFE finishing path, preserving painting timestamps. RIFE frames never enter generation. Motion settles before 13.5s. The final native hold is half a second at two paintings/s, or a quarter-second at uniform four/s.
- Prompt events are at **0, 2, 3, 4, 5, 7, 8, 9, 10 seconds**: frames 0, 48, 72, 96, 120, 168, 192, 216, 240. Each event replaces the preceding scene description. Hold it until the following event; hold the last through the ending.
- For each sequence, the complete positive prompt is **the event paragraph followed by its fixed style paragraph**. Use opening plus style for the initial generation too. The paragraphs describe an image that could exist at that instant; they contain no editing commands or references to a previous frame.
- Keep prompt timing independent of the main agent's noise/CFG/Euler schedules. The three intermediate descriptions in each transition must not inadvertently restart a noise ramp. Leave sampler choices to the technical experiment; this document proposes no additional sweep.

### Prompting and reference basis

Verified the official [Krea prompting guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md) and its linked [prompt expansion instructions](https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt) on 2026-09-14. The supplied `docs/prompting-guide.md` URL returns 404. Krea recommends natural language and detailed descriptions; its expansion instructions emphasize grounded composition, relationships and a cohesive paragraph. The prompts below are original authored descriptions. Keep their final expanded text fixed for reproducibility; no automatic embellishment is needed. The official guide does not validate recurrent animation or the proposed semantic bridges.

The [accepted dynamic journey](../dynamic-journey.md) supports changing entire environments, while its inherited arches and crowded later compositions argue for deliberately opening the view. The [BonsAi reference study](../../../../../../docs/research/bonsai-effect-workflow.md) motivates readable silhouettes, changes of scale and purposeful movement. This plan uses the current 2D warp controls; it does not reproduce the reference's depth/guide-flow mechanism.

## 1. Velvet Flood

**An empty crimson theatre grows into a giant mushroom wetland; the wetland opens into a black sea of red sailing ships.** Enclosure → organic landscape → exposed horizon. Velvet folds become stalks and gills; mushroom caps become fabric canopies before they read as sails. The environment changes along with the material.

The appeal is an extravagant, dark fairytale: saturated oxblood and cherry red, charcoal water, pale pink light, occasional mint-green moss. Deep shaded volumes, wet surfaces and large silhouettes carry the detail. The ending should feel spacious and windswept.

**Fixed style paragraph:**

> A richly textured surreal cinematic painting with deep sculptural shadows and physically convincing surfaces. Oxblood red, cherry lacquer, charcoal black and pale rose light dominate, with small mint-green accents. Broad readable silhouettes sit against spacious areas of shadow or sky; tactile folds, ridges and reflected light supply the fine detail. Wide landscape composition.

### Timed image descriptions

**0.0–2.0s — Opening: the flooded theatre.**

> Inside an immense empty theatre, viewed from just above a glossy black stage floor. Two heavy oxblood velvet curtains stand apart at the left and right edges, their thick pleats catching narrow rose-white highlights. A scalloped crimson valance hangs across the upper edge. Beyond the open curtains, a broad shallow pool covers the stage and reflects a pale pink cyclorama. Three low semicircular stage steps stretch across the bottom of the image. The open middle occupies half the view, with the curtains forming tall sculptural sides. Worn velvet pile, lacquered wood, tiny water ripples and long reflections are sharply tangible in the theatrical side light.

**2.0s — Fabric with living ribs.**

> An open crimson theatre with thick curtain columns at both sides of a broad black pool. The lower curtain folds have pale fleshy ribs and rounded roots resting on the wet stage. Broad red shelves project from the upper pleats, their undersides finely lined like mushroom gills. The low stage steps carry small patches of mint-green moss. Pale rose mist fills the open central stage beneath the scalloped velvet valance.

**3.0s — A fungal stage.**

> A shallow black pool lies between two clusters of enormous red mushrooms. Their tall pale stems carry vertical velvet pleats, and their broad cherry-red caps have scalloped edges and luminous pink gills. A few short hanging curtain folds remain along the upper corners. Moss-covered semicircular terraces occupy the foreground, with irregular gaps of water between them. Open rose-colored fog extends far behind the mushroom stems.

**4.0s — The theatre is almost a wetland.**

> A marsh of towering crimson mushrooms surrounds an open black-water channel. Large flattened caps overlap along the upper sides while pale ribbed stalks stand on irregular mint-green moss islands. Low curved remnants of lacquered stage steps sit at the near waterline. The distant center is a pale misty horizon; slender mushrooms recede into it at different sizes. Rain beads cling to the red caps and their delicate pink gills.

**5.0–7.0s — Scene two: the mushroom wetland.**

> At water level in a vast mushroom wetland, a broad reflective channel runs from the lower center toward a low rose-gray horizon. An enormous cherry-red mushroom rises on the left, its wide cap and luminous pleated gills silhouetted against mist. Smaller mushrooms stand far apart on low mint-green moss islands to the right. Pale stems, black water and deep reflections form clear vertical shapes. Large spaces between the islands reveal the distant landscape under a soft pink overcast sky.

**7.0s — Caps stretched into canopies.**

> A black-water wetland holds widely separated red mushrooms on long narrow moss islands. Several caps have tall angular ridges and stretched triangular panels, with thin pale ribs visible underneath. The largest red canopy on the left leans diagonally above a straight ivory stem. Dark water occupies most of the lower half, and long ripples cross the increasingly open spaces between islands. A pale rose-gray sky spans the distance.

**8.0s — Living sailing structures.**

> Three narrow dark islands sit low in a broad expanse of black water. Each carries a tall pale pole and an angular crimson canopy with taut fabric panels and fine radial seams. The left canopy retains a small rounded mushroom edge beneath its pointed red upper sail. Its island has a raised bow-like end and a thin moss-covered rim. Wide strips of open water separate these structures beneath a low pink-gray sky.

**9.0s — Ships with the last fungal traces.**

> A charcoal sea stretches to a low unobstructed horizon. A dark sailing vessel in the left middle distance carries a broad triangular oxblood sail on an ivory mast. The sail's lower edge has a soft scallop, and its underside shows delicate pink gill-like pleats. Two smaller red-sailed vessels sit far apart near the horizon. Thin green moss traces the nearest hull while pale wakes spread across the black water under rose-gray storm clouds.

**10.0–14.0s — Scene three: the open sail sea.**

> An open charcoal ocean under a vast pale rose-gray storm sky. A single dark sailing ship sits left of center in the middle distance, its tall ivory mast carrying one broad oxblood triangular sail with deep velvet folds and fine wet seams. Two much smaller red sails punctuate the far horizon on the right. Long silver-pink wakes cross the foreground water diagonally. The sky fills the upper half, and open sea surrounds the ships on every side. Cold side light catches rain droplets along the nearest sail's clean silhouette.

### Bounded movement phrases

Use the existing eased phrase composition. Centers below are fractions of **image width/height**; travel is screen-content displacement in those same units. Scale is the total multiplicative change over the phrase, and turn is the total localized twist. Each phrase eases into and out of movement, then stops accumulating.

| Time | Visual purpose | Center x,y; radius / H | Scale; turn | Travel x/W,y/H |
| --- | --- | --- | --- | --- |
| 0–2s | Approach the open stage; gently flex the left folds. | 0.23,0.48; 0.48 | 1.08; +8° | +0.015,0 |
| 1.8–5.2s | Bow the right-hand curtain/caps outward as the stage acquires depth. | 0.77,0.42; 0.48 | 0.96; −18° | −0.03,+0.01 |
| 5–7.5s | Glide sideways across the channel; retain the large left mushroom. | 0.28,0.43; 0.50 | 1.04; +6° | +0.05,0 |
| 7.3–10.5s | Tilt the canopy field into a sail diagonal. | 0.36,0.40; 0.48 | 1.02; −12° | −0.035,+0.015 |
| 10.2–13.3s | Ease wider as open water becomes the dominant space. | 0.50,0.58; 0.65 | 0.92; 0° | 0,+0.015 |

**Likely semantic failure:** the theatre remains a proscenium all the way through, or the ending reads as mushrooms on boats. The decisive changes are loss of the overhead enclosure by 5s, then thin masts, triangular sails, separate hulls and a continuous sea by 10s. More red texture alone is insufficient. If the main agent revises one bridge, prioritize a flatter cap with a visible triangular fabric panel at 7–8s; do not keep adding theatrical nouns to the final prompt.

**Likely motion/interpolation failure:** twisting a tall stem can kink it, and a mast or fine gill pattern may double in RIFE. Keep the main mushroom and later sail inside the central 80% of the frame. The final widening is a modest 2D scale change; it cannot reveal genuinely hidden scenery. Inspect the raw 7–10s paintings before interpreting a smooth-looking RIFE dissolve as a successful morph.

## 2. Porcelain Weather

**A monumental blue-and-white wave becomes a folded mountain valley; the mountain ridges lift into an open sky of giant origami cranes.** Low ocean view → elevated terrain → aerial space. Foam ridges become paper strata; folded peaks become wings. The final scene deliberately releases the ground instead of retaining another tunnel or skyline.

This is bright, crisp and tactile: chalk white, hand-painted ultramarine, tiny coral-red accents and soft gray-blue shadows. Ceramic glaze gives way to fibrous paper. It offers a substantial palette and material change from the brass/desert work and from Velvet Flood.

**Fixed style paragraph:**

> A surreal handmade miniature photographed with crisp sculptural detail and deep focus. Chalk-white surfaces carry flowing ultramarine brushwork and a few small coral-red accents. Grazing cool daylight reveals glaze cracks, pressed ridges or paper fibers appropriate to each material, with strong soft-edged blue-gray shadows. Spacious, asymmetrical wide landscape composition and restrained color.

### Timed image descriptions

**0.0–2.0s — Opening: the porcelain tide.**

> A colossal breaking ocean wave made of white glazed porcelain rises diagonally from the lower left toward the upper middle of the image. Its long crest has torn, foam-like white edges, and hand-painted cobalt currents sweep across its deep curved face. The wave forms one broad open curve above a dark ultramarine trough. Low broken foam plates spread across the near water. On the right, a wide strip of calm sea reaches a pale almost-white horizon beneath a small coral-red sun. Fine glaze crackles and sharp rim highlights make the impossible ceramic water feel heavy and tangible.

**2.0s — Porcelain water with folded edges.**

> A broad white porcelain wave rises on the left above an ultramarine trough. The torn crest consists of overlapping angular plates with folded edges, cobalt bands and a few exposed matte white fibers. The lower wave face has long shallow horizontal shelves between glossy blue channels. Calm pale water and a small coral-red sun occupy the open right side. Cool light casts distinct shadows beneath the raised crest plates.

**3.0s — Wave-shaped terrain.**

> A tall white ridge shaped like a breaking wave overlooks a narrow cobalt water channel. Its steep face consists of stacked angular shelves with folded paper edges and isolated patches of glossy porcelain. Low terraced foothills fill the lower left, while the channel bends toward open pale space on the right. Blue brush-painted lines follow the contour of every ledge. The highest crest is sharply creased and casts a broad shadow onto the terraces below.

**4.0s — A dry folded valley.**

> An elevated view across a white folded-paper mountain valley. A high ridgeline rises on the left with a few curved porcelain overhangs near its summit. Layered angular terraces descend toward a narrow ultramarine river running diagonally through the center. Broad dry paper shelves occupy the foreground, their fibrous cut edges catching cool daylight. A second lower ridge lies on the right beneath a pale sky and a small coral-red sun.

**5.0–7.0s — Scene two: the paper mountains.**

> A vast mountain valley built from thick folded white paper, viewed diagonally from above. A tall jagged ridgeline occupies the left, and lower terraced slopes recede across the right. A narrow ultramarine river threads through the deep central valley. Bold cobalt brushwork follows the mountain contours; crisp folds cast long blue-gray shadows. The foreground consists of broad exposed paper ledges with visible fibers. The pale sky and a small coral-red sun occupy the upper quarter of the composition.

**7.0s — Mountain creases shaped like wings.**

> A white paper mountain valley with broad triangular folds rising from its left ridge. Two adjoining folds extend sideways like open wings while their bases still join the terraced slope. Cobalt lines run along the sharp creases. Small triangular sheets hover just above the far peaks, with pale sky visible underneath them. The ultramarine river remains in the lower valley, and the coral-red sun sits in the pale distance.

**8.0s — Partly detached paper birds.**

> Enormous white origami bird forms rise above a folded mountain ridge. The nearest has two wide angular wings and a pointed folded neck, while its long lower paper tail still joins a narrow peak at the bottom left. Two smaller folded forms float farther away, separated from the terrain by open pale sky. Cobalt contour lines cross the white wing panels. The mountains occupy the lower third, with the blue river visible as a thin distant thread.

**9.0s — Sky between the forms.**

> A huge white origami crane floats diagonally left of center against a pale sky, its broad angular wings marked with ultramarine brush lines. A long folded tail points down toward a small detached paper ridge near the bottom edge. Two smaller cranes float far away on the right. Wide areas of empty sky separate the birds and the remaining paper fragments. A small coral-red sun balances the composition near the upper right.

**10.0–14.0s — Scene three: the origami sky.**

> High in an immense pale almost-white sky, one monumental white origami crane floats diagonally across the left middle of the view. Its broad folded wings, pointed neck and long angular tail form a clean unmistakable silhouette. Hand-painted cobalt lines follow its creases, and cool light reveals the fibers and thickness of the paper. Two much smaller cranes float far away on the right beneath a small coral-red sun. Soft detached cloud wisps sit near the lower edge. Open sky surrounds every bird, creating a strong sense of scale and height.

### Bounded movement phrases

Use the same units and easing convention as Velvet Flood. The shifts create changing framing in a flat warped image; the prompts request the changing viewpoint and depth cues.

| Time | Visual purpose | Center x,y; radius / H | Scale; turn | Travel x/W,y/H |
| --- | --- | --- | --- | --- |
| 0–2s | Rise slightly along the wave face while its crest bends. | 0.28,0.39; 0.52 | 1.06; −10° | +0.01,+0.03 |
| 1.8–5.2s | Open the crest into diagonal terraces. | 0.30,0.45; 0.52 | 0.96; +16° | −0.025,+0.015 |
| 5–7.5s | Traverse the valley while the large left ridge stays readable. | 0.64,0.68; 0.55 | 1.04; −6° | −0.05,0 |
| 7.3–10.5s | Lift the wing-shaped ridge into the open center. | 0.36,0.42; 0.48 | 1.02; +12° | +0.035,−0.035 |
| 10.2–13.3s | Ease wider around the crane and let its silhouette settle. | 0.45,0.44; 0.60 | 0.92; 0° | +0.01,+0.01 |

**Likely semantic failure:** the valley remains a ceramic wave, or the final cranes look like mountains with beaks. The 3–4s prompts introduce dry horizontal ledges, a narrow river and an elevated view to establish land. The 8–9s prompts introduce sky underneath separate forms and a visible folded neck to establish flight. A bird merely printed on a mountain does not satisfy the final scene. This second transition is the higher-risk semantic leap of the two proposals.

**Likely motion/interpolation failure:** a regional twist may curve the straight origami edges, and narrow tails can duplicate or disappear between paintings. Preserve a broad wing silhouette and roomy framing; avoid extra motion on the final crane. Repeated fine cobalt lines may boil even when the big form holds. The apparent rise from ocean to aerial view is an artistic transformation, not a verified 3D camera move.

## Small handoff and selection criteria

The main agent needs one generated opening, one nine-event prompt schedule and one five-phrase motion list for the selected sequence. Use its current session runner and output ownership; the historical `dynamic_journey.py` opening-copy path is tied to the old saved snail image and must not be treated as a fresh-opening generator.

The inspected existing transform localizes **twist** with a Gaussian radius; scale and travel affect the whole image. The tables rely only on those controls, with no subject masks, segmented protection, depth model or new guide video. In the historical phrase format, `zoom = scale − 1`; coordinates and travel are normalized by image height, so multiply the tables' x/W values by W/H when translating them. `turn` and `radius` use the stated degrees and height units. Treat these modest numeric amplitudes as proposed starting values, not visually validated settings.

Prefer **Velvet Flood** for the first creative render: folds → gills → stretched fabric offer concrete intermediate surfaces, and the black sea provides a clear final release from the enclosed opening. **Porcelain Weather** is the contrasting option if the main agent wants brighter graphic imagery and accepts the greater mountain-to-bird risk.

Screen the opening before continuing. At roughly 1.5s, 6s and 12s, three sampled paintings should independently read as the three named environments. Inspect every raw painting across 2–5s and 7–10s: several different structural intermediate states should be visible, with readable forms during the scene holds. Then inspect corresponding RIFE intervals for doubled edges. A pleasing clip may still contain an abrupt transition; record that separately from creative preference. All selection and rendering remain with the main agent.
