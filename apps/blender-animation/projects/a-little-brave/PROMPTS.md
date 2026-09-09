# Still artwork provenance

All artwork uses the built-in image generation tool. Images supply painted textures only; Blender authors animation. Original tool outputs are retained and copied into this project's ignored `assets/` directory.

## Rottweiler atlas, v001

Inputs: puppy-2d/output/v011/frames/frame_0001.png (style) and puppy-2d/assets/parts-atlas-v001.png (layout).

Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-efca99fc-29af-4981-b3b5-210523b08199.png`, copied to `assets/rottweiler-atlas-v001.png`.

Exact prompt:

Use case: illustration-story. Asset type: transparent 2D animation character parts atlas, six separate fully isolated parts in a clean 3-column by 2-row layout. Image 1 is the established puppy film's style reference. Image 2 is ONLY an example of the six-part atlas layout. Create a DIFFERENT character: a large, powerful adult Rottweiler, charcoal-black short coat with rich warm rust-tan muzzle, small tan eyebrow marks, tan lower legs, a broad deep chest and square heavy muzzle. Clearly mature and imposing in build, but with calm thoughtful brown eyes and a gentle closed-mouth expression; no aggression, no teeth. Match the puppy reference's precise warm brown contour drawing, restrained two-tone cel shadows, clean hand-drawn feature animation quality. Profile facing RIGHT, flat side-on orthographic drawing, consistent coat colors and scale among parts. Top row: 1) torso only from rump to a generous upward neck stump, no head, legs or tail; include a substantial neck that can overlap behind the jaw; 2) entire head with broad square muzzle and natural adult proportions, NO EARS, generous fur below the jaw for overlap; 3) one short triangular folded ear, black with warm charcoal inside, rounded triangular tip, isolated. Bottom row: 4) one complete near front leg from thick shoulder through elbow to tan paw, modest natural standing bend, 3 visible toes; 5) one complete near hind leg with robust haunch, hock and tan paw, natural standing bend; 6) one intact natural long Rottweiler tail, tapering, relaxed upward curve, charcoal, no docking. The torso and head are adult broad shapes, not a puppy merely recolored. Actual TRANSPARENT background with alpha, no glow, no shadows outside the parts, no text, no labels, no grid lines, no frames. Each of the six parts must have wide clear separation and no clipping. These are final painted textures for a native Blender 2D rig, not a completed dog illustration.

## Park background, v001

No input reference. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-19e3c25d-b33c-4a39-b968-f3b7e7e8e467.png`, copied to `assets/park-v001.png`.

Exact prompt:

Use case: illustration-story. Asset type: final background painting for a 16-second hand-drawn animated short. A beautiful quiet dog park in late-afternoon sunlight, warm painterly Japanese feature-animation background sensibility, delicate gouache texture, lovingly observed trees and foliage, balanced and cinematic, crisp detailed painting rather than photorealism. Wide 16:9 landscape composition. Low dog-height viewpoint across a level warm ochre sandy clearing. The broad central and lower stage, from 20% to 85% of image width and roughly 55% to 85% of image height, is open uncluttered light sandy ground where two animated dogs will stand. Keep this playing surface flat and readable, no objects in it. A modest old wooden fence follows the far edge of the park around the middle height of the image, an open gate toward far left, a simple empty bench off to the far right in the background, and rich leafy trees framing the left and right upper corners. A sunlit canopy, luminous distant meadow and soft pale blue sky, subtle atmospheric depth. Light comes from upper left, gentle golden highlights with soft cool green shade. Interesting asymmetrical natural composition, not a symmetrical stock park. Tiny grass tufts and a few daisies along the very bottom corners only. No people, no animals, no balls, no text, no watermarks, no modern logos. The background is an empty animation set; leave breathing room for large character silhouettes in the central clearing. Full-bleed finished background painting.

## Atlas transparency edit, v002

Input: `assets/rottweiler-atlas-v001.png`. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-286524cb-2690-4a50-97af-f71120c34cdf.png`, copied to `assets/rottweiler-atlas-v002.png`.

Exact prompt:

Use case: background-extraction. EDIT TARGET: the attached six-part Rottweiler animation atlas. Remove the entire gray-and-white checkerboard background and all pale speckling between the six dog parts. Return an actual RGBA PNG with a genuinely TRANSPARENT alpha channel outside the six parts. The checkerboard in the input is unwanted painted pixels, not part of the artwork. Preserve every dog part's contour, color, shading, position, size, and the original 1536 by 1024 layout. Do not redraw or redesign the dog. Clean antialiased edges. No opaque background of any color, no simulated transparency/checkerboard, no glow, no border, no labels. Six isolated opaque dog parts on actual transparent alpha.

## Atlas chroma-key edit, v003

Input: `assets/rottweiler-atlas-v002.png`. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-f5cf7bc7-4679-4888-9d8d-98940c3fa423.png`, copied to `assets/rottweiler-atlas-v003.png`.

Exact prompt:

Use case: precise-object-edit. Edit the attached six-piece Rottweiler parts atlas. Replace ALL gray/white checkerboard pixels outside the dog parts with one perfectly uniform saturated MAGENTA background, exact RGB (255,0,255), hex #FF00FF. This is a chroma-key sheet, so the background must be a completely flat solid magenta with absolutely no checkerboard, transparency, texture, glow, gradients, speckles or shadows. Preserve the six dog parts, their positions, dimensions, silhouettes and original colors exactly. Do not add magenta inside the opaque dog artwork, and keep the white eye highlight white. Clean precise antialiased contours. Maintain the 1536x1024 six-part layout. The result should look like the same illustration cutouts on a perfectly flat bright magenta canvas. No labels or other content.

## Rottweiler paw

Input: `assets/rottweiler/front_leg.png`. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-fe5e5f86-7c6c-4aca-ae40-0987357d6674.png`, copied to `assets/rottweiler-paw-source.png`.

Exact prompt:

Use case: illustration-story. Asset type: one isolated paw drawing for a 2D animation rig. Reference image is the Rottweiler's front leg and establishes the exact warm rust-tan paw color, black outline, dark small nails, and cel shading. Draw ONLY the paw, without the leg, wrist, ankle or any vertical stump. Side profile facing RIGHT: a sturdy low rounded oval paw resting flat on the ground, three visible toes with small dark nails, compact adult Rottweiler proportions. A little extra rounded coverage on its upper left is needed to overlap a separately animated wrist. Match the reference's clean warm hand-drawn contour and precise restrained cel shading. Put the single paw centered on a perfectly uniform saturated MAGENTA background RGB (255,0,255), #FF00FF, with generous empty margin. No checkerboard, no transparency simulation, no text, no ground line, no cast shadow, no glow. One paw only.

## Rottweiler folded front leg

Input: `assets/rottweiler/front_leg.png`. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-d8908e1c-5712-408b-b658-3ee522497817.png`, copied to `assets/rottweiler-bow-source.png`.

Exact prompt:

Use case: illustration-story. Asset type: replacement front-leg drawing for a 2D Rottweiler animation rig. The reference is the standing front leg; match its exact charcoal upper coat, rich rust-tan lower leg, dark nails, contour style, shading and sturdy adult thickness. Draw that same single FRONT leg in a deep friendly play-bow pose, side profile facing RIGHT. The upper arm descends almost vertically from a generous rounded shoulder attachment at TOP LEFT, bending at a low elbow near BOTTOM LEFT. From that elbow the forearm extends nearly horizontally to the RIGHT along the ground and ends in the same tan paw resting flat at BOTTOM RIGHT, with 3 visible toes. This is a clearly L-shaped bent foreleg, NOT a rear leg. Smooth fleshy elbow, no sharp polygon corner, natural dog anatomy. No body, no head, no other legs. Fill most of a square image with generous margins. Perfectly uniform solid MAGENTA backdrop, exact #FF00FF, no checkerboard, no shadows, no texture outside the leg, no text. Final clean painted part for a rig.

## Rottweiler blink

Input: `assets/rottweiler/head.png`. Output: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-e43b9dae-96a7-448f-8015-1f420bac7514.png`, copied to `assets/rottweiler-blink-source.png`.

Exact prompt:

Use case: precise-object-edit. EDIT TARGET: the attached isolated Rottweiler head. Change ONLY the visible eye: close it into a soft contented eyelid curve, like a trusting brief blink. Preserve the exact head silhouette, mouth, expression outside the eye, muzzle, nose, fur markings, colors, shading, canvas dimensions and position. Keep the perfectly flat MAGENTA #FF00FF background. Do not change the eyebrows, cheek shape, neck fur, lighting, mouth opening or any other region. This is one replacement eye drawing for the exact same animation character. No additional objects, no text.
