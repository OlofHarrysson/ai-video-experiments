# Two concepts for the $10 filmmaking session

Proposed creative directions, not rendered results. Main owns execution, shortlist selection and the **$10 cap on new cloud spend**, including setup/idle time. Start with **The Clock Learns to Crawl**; use **The Drowned Parasol** for a visually distinct alternative. Avoid a tedious succession of owl heads, cyan eyes and concentric porcelain cathedrals. Distinction should come from subject, silhouette, composition and material, not merely different prompt wording.

Grounding: [taste journal](../../../../../docs/olof-learning-journal.md), [Tomorrow](../../reference-studies/references/tomorrow.md), [Brain Entity](../../reference-studies/references/brain-entity.md), [Child of the Moon](../../reference-studies/references/bonsai-child-of-the-moon.md), and [prompting notes](../../../../../docs/research/prompting-for-feedback.md). Borrow readable visual metaphors, designed large shapes and expressive regional motion. Recent local evidence supports bounded motion followed by a positive-prompt transformation; it does not establish arbitrary object replacement.

## Shared execution brief

Use Krea, recurrent warped-previous-painting initialization, Lanczos, native **24 fps / repaint every 0.5s (cadence 12)** and existing RIFE finishing. Keep main's current sampling recipe fixed. Half-second repainting is the latest authorized faster direction; earlier one-second taste notes are not a reason to override it. Motion amounts below are **total shot displacements**, not per-frame increments. Main maps these artistic targets onto existing controls; do not introduce a new depth/flow system for them.

Freeze two descriptive positive prompts per concept: opening/current scene and target scene. Switch text at the stated repaint; do not repeatedly request camera moves in the text after applying them to pixels. Ease spatial velocity continuously to zero before sustained target repainting. Holding the spatial path still permits diffusion to change geometry. Preserve each painting and choose a usable source range if the last repaint is weaker.

## 1. The Clock Learns to Crawl — warm, dry, graphic

**Beat:** an instrument measuring time becomes an animal taking its time. A single large brass pocket watch on a dark stone ledge becomes a land snail. Ochre, oxblood and charcoal; engraved black contours and broad quiet background. Whole creature in side view, not another frontal face.

**Opening prompt**

> A surreal illustration of one large antique brass pocket watch resting at a slight diagonal on a charcoal stone ledge. Its round amber dial faces the viewer in three-quarter view, with two dark hands and simple engraved tick marks. A loose brass chain curves along the ledge toward the right. The watch occupies the middle-left of a wide composition, with open space along the ledge on the right. Behind it, spare ochre dunes recede beneath an oxblood dusk sky. Low golden side light catches the worn metal rim and casts a long dark shadow. Bold etched black contours, delicate engraved textures, tactile shaded metal and restrained washes of warm color.

**Transition prompt**

> A surreal illustration of one large land snail resting on a charcoal stone ledge, its head extending toward the right. A rounded amber-and-brass spiral shell occupies the middle-left of the wide composition. The shell has deep sculpted coils, fine radial engravings and worn golden highlights. An elongated dark red body emerges beneath it, with a broad muscular foot touching the stone and two slender raised eyestalks. The whole snail is clearly readable, with open space in front of its head. Spare ochre dunes recede beneath an oxblood dusk sky. Low golden side light models the shell, moist body and long shadow. Bold etched black contours, delicate textures and restrained warm washes.

**8s spatial phrase:** 0–1.5s, the region around the dial curls clockwise and swells gently, drawing attention into its round form; target about 12 degrees of local turn and 8% enlargement in total. From 1.5–2.5s, smoothly decelerate both components to a full stop. Keep the ledge legible and reserve the right third for the emerging head. First snail-conditioned painting at **3s**; hold spatial framing through 8s. Final painting at 7.5s, then the usual half-second native hold. One opening plus 15 repaints, if main uses this duration unchanged.

**Likely bridge:** round dial → coiled shell; chain/ledge contours → an emerging elongated body. This is an affordance, not a demanded pixel correspondence. The new prompt supplies the diagnostic anatomy that the old object lacks.

**Risks / shortlist test:** a watch with decorative spiral marks is not yet a snail. Require a coherent body, foot and eyestalks beneath/beside the shell. Chain fragments may become extra limbs; engraved dial geometry may stubbornly persist. Reject a beautiful shell-only ending or an opening too tightly cropped to permit a head. No need for legible numerals. Favor one frame range where the viewer can identify both endpoints without reading labels.

## 2. The Drowned Parasol — dark, translucent, vertical

**Beat:** a shelter becomes a creature. One red parasol suspended underwater becomes a luminous jellyfish. Cherry red, rose, pearl and near-black plum; soft light through layered surfaces and a tall descending silhouette. A spacious underwater setting separates this from the dry, engraved first concept.

**Opening prompt**

> A dreamlike underwater painting of one open red silk parasol suspended above pale rippled sand in deep still water. Seen slightly from below, its broad domed canopy occupies the upper middle of a wide composition, with scalloped fabric edges and fine dark ribs radiating from its center. A slender curved handle hangs into the open lower half of the image. Rose light shines through the cherry-red silk, revealing overlapping translucent folds and glossy droplets along its edge. Sparse drifting particles catch the light. The distant water falls into near-black plum shadow. A clear solitary silhouette, sculptural fabric, luminous layered color and generous quiet space around the parasol.

**Transition prompt**

> A dreamlike underwater painting of one large crimson jellyfish floating above pale rippled sand in deep still water. Seen slightly from below, its translucent domed bell occupies the upper middle of a wide composition. Rose light glows through folded membranes and pearl-white radial canals beneath the red bell. A scalloped soft rim surrounds the dome; several long delicate tentacles and broad ruffled oral arms descend through the open lower half of the image. The jellyfish has a clearly readable bell and flowing suspended appendages, with luminous tissue and fine internal structures visible through its body. Sparse drifting particles, near-black plum water and generous quiet space surround its solitary silhouette.

**10s spatial phrase:** 0–2s, lift the composition gently by at most 5% of frame height while opening the canopy region outward by about 8%; a shallow local fan/curl gives the ribs an unfolding motion. Avoid twisting the whole image into a vortex. From 2–3s, ease both travel and regional expansion to zero; leave at least the lower third available for the tentacles. First jellyfish-conditioned painting at **3.5s**, after the path settles. Hold spatial framing through 10s. Final painting at 9.5s, followed by a half-second native hold. One opening plus 19 repaints if used unchanged.

**Likely bridge:** parasol dome/ribs → jellyfish bell/radial canals; handle and hanging folds → descending appendages. Shared geometry should offer an easier transition than inventing a completely unrelated body plan while retaining the scene.

**Risks / shortlist test:** the result may remain an umbrella with dangling ribbons. Require a soft biological bell and several distinct tentacles/oral arms rather than one surviving rigid handle. Thin appendages may double or blur under RIFE; inspect anchors and the finished transition separately. Dark water may become muddy, so the opening must already have a strong rim and translucent interior. A vertically cropped creature or a flat red disc is not a successful ending.

## Selection and stopping

These are two candidate shots, not a parameter sweep. The full proposed pair is **36 diffusion calls including two openings**, before retries; that count is not a cost guarantee. Main should screen each opening for composition before committing its continuation and use observed spend to decide whether both fit the remaining cap.

Shortlist by readable transformation, sustained material depth, expressive opening movement, a settled recognizable ending and finished playback. A strong 5–7s usable excerpt is preferable to retaining a weak tail solely to reach the proposed duration. Present the best shot first and the second only when its distinct visual idea works. Do not spend the remaining budget polishing tiny ornamental differences or producing more owl/cyan variants.
