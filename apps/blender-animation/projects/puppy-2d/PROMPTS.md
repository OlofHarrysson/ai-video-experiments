# Artwork provenance and exact prompts

Four successful calls to the built-in `image_gen` tool, 2026-09-09. No CLI/API fallback and no image-to-video generation. Every output was inspected and copied into `assets/`. Cropping extracts isolated components and preserves generated RGBA pixels. Native Blender materials mask attachment regions and the eye replacement; animation uses mesh deformation and discrete visibility keys.

## 1. Parts atlas

Output: `assets/parts-atlas-v001.png`. Original: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-2abeb00b-ff79-4d2f-a67f-379693052b0f.png`.

The requested cyan backing was not returned; the output instead contains usable transparency. Its RGB values outside the alpha silhouette include dark glow-like colours, which are invisible when composited using its alpha. No chroma-key extraction was needed.

```text
Create one production-quality 2D animation CHARACTER PARTS ATLAS, landscape 1536x1024. A charming original golden honey-and-cream floppy-eared puppy, warm hand-drawn Japanese feature-animation sensibility, confident delicate dark-brown ink outlines, beautifully designed curves, flat cel colors with one restrained warm shadow tone, no 3D rendering, no texture noise, no gradients. STRICT isolated flat pieces on uniform solid saturated CYAN #00FFFF background, no shadows cast onto background, NO text, NO labels, NO borders. Arrange EXACTLY SIX well-separated components in a regular 3-column by 2-row grid, each contained in its cell with large cyan padding, none touching another piece. All parts form the SAME small puppy viewed in clean SIDE PROFILE FACING RIGHT, slight 3/4 view of face only for charm. Top LEFT: the puppy's plump bean-shaped TORSO ONLY, tan back and cream chest/belly, no head, no legs, no tail, no face, upper-right neck connection gently rounded. Top MIDDLE: the puppy's complete adorable oversized HEAD facing right, lively dark expressive eye with catchlight, cream cheek and muzzle, round dark nose, little smiling closed mouth, NO EARS, no neck or torso. Top RIGHT: ONE long floppy cocoa-brown EAR, rounded teardrop, root at top, curved and expressive, isolated. Bottom LEFT: ONE complete FRONT LEG, tan upper leg, slightly backward-bending elbow in its middle, cream rounded generous paw at the bottom pointing RIGHT, upper attachment broad and smoothly rounded, lower leg mostly vertical. Bottom MIDDLE: ONE complete HIND LEG, tan round generous haunch on top, forward-bending knee and backward-bending hock, cream rounded paw at bottom pointing RIGHT. Bottom RIGHT: ONE upward-curving tapering tan TAIL with subtle cream tip, thick attachment at lower-left and tip extending upper-right. Beautiful professional animation cleanup drawing, consistent outline width across all six pieces. Ensure no stray bits, no complete dog, no additional poses or duplicate parts. This is functional layered puppet artwork, not a diagram with labels.
```

## 2. Expression replacement

Reference/edit target: `assets/head.png`, extracted from the atlas. Output: `assets/head-delighted-source.png`; trimmed derivative: `assets/head-delighted.png`. Original: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-11197ab6-f275-4949-a12a-a5c52cd7be50.png`.

The final scene uses only the eye region of this drawing as a masked overlay. The initial full-head swap changed the silhouette/colour slightly, so the original head remains visible throughout.

```text
Edit this exact puppy head for a 2D animation expression replacement. Keep EXACTLY the same head outline, nose position, muzzle outline, cheek, hair tufts, proportions, camera, colors, shading, canvas framing and TRANSPARENT background. Change ONLY the facial expression: the eye is closed in a joyful soft upward crescent with a confident dark brown ink line, and the mouth is a small open delighted puppy grin with a little pink tongue. Absolutely preserve the silhouette and face landmarks. Still NO ears or neck or body. The result must look like the exact same cel drawing with only eye and interior of mouth redrawn, suitable for swapping over the original animation head. No background, no glow, no added objects.
```

## 3. Folded front leg

Reference/edit target: `assets/front_leg.png`. Output: `assets/front-leg-bow-source.png`; trimmed derivative: `assets/front_leg_bow.png`. Original: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-49ed0d5a-1f7a-4a9c-9e9e-e23f0217d927.png`.

The final uses the folded limb above the foot. The common paw drawing below is shared across the normal and folded variants.

```text
Create a replacement cel drawing of this SAME puppy FRONT LEG in a deep PLAY BOW pose. Only ONE isolated leg on genuinely TRANSPARENT background. Same golden tan coat, cream rounded paw, exact delicate dark-brown line style, flat warm cel shading. The upper attachment is broad and rounded at the TOP CENTER. The upper arm slopes diagonally DOWN LEFT from the shoulder to a rounded ELBOW at the BOTTOM LEFT. The forearm then extends HORIZONTALLY RIGHT along the floor to a generous cream puppy PAW at the BOTTOM RIGHT. The flat sole of the paw rests on the same horizontal floor level as the elbow. The foot points RIGHT and is shaped naturally with three rounded toes. A clean readable bent L-shaped silhouette with the elbow pointing LEFT; visible empty space above the horizontal forearm. No hand, no second leg, no whole dog, no labels, no background, no shadows. This must be a polished animation replacement for the fully folded leg, with a natural stable paw that will not need stretching. Preserve the character's drawing design.
```

## 4. Shared isolated paw

Reference/edit target: `assets/front_leg.png`. Output: `assets/paw-clean-source.png`; trimmed derivative: `assets/paw_clean.png`. Original: `/Users/olof/.codex/generated_images/01a08545-88e4-79c2-85d8-ae4f36c696de/exec-98b5e5ce-be05-41c7-a492-6181ac595237.png`.

```text
Draw ONLY a single isolated cream-colored puppy PAW/FOOT from this character, facing RIGHT, on truly TRANSPARENT background. It must be a complete closed rounded silhouette: a squat softly rounded oval bean, flat sole, three rounded toes toward the right, gently curved top. NO leg, NO vertical ankle, NO straight cut-off top, NO stump, NO disconnected bits. The foot should be about 1.8 times wider than tall. Cream fur, just a tiny warm tan shading toward the left rear of the foot, delicate dark-brown ink contour and two elegant short toe-separation lines, same exact professional 2D animation style as the reference. Make the top outline fully curved and natural so an overlapping leg can meet this foot from any angle without showing a cut edge. One foot only. No background, no ground shadow, no text.
```
