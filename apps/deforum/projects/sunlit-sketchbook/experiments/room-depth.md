# Room depth and reference-guided art direction

2026-11-11. Candidate room-v003 is ready for Olof’s review. Two new still attempts; no new animation or audio.

![Recommended opening candidate](../runs/room-v003/image.png)

## Intent

After the first ten-second cut, Olof asks for more purposeful motion and storyboarding, and says our artwork feels flat compared with the original’s detail. He agrees to remake one room still using an actual source-film frame for lighting, texture and depth before rebuilding the other shots. The [revised storyboard](storyboard-v002.md) incorporates a camera push and a galaxy reveal.

## Inputs and method

Both attempts use Fal’s current recommended `google/nano-banana-2.1/edit` endpoint, high thinking, 2K, landscape 16:9, one PNG per request. This extends the earlier text-reconstructed look study with actual source-image conditioning. It does not establish how the original film was made.

The style/layout reference is Shuvfx’s Do It Big frame 95 at 3.958333 seconds from the preserved 576p rendition: `references/assets/frame-reviews/v002/frames/000002.png`, SHA-256 `58df627daec3fc46fa313e458fc0efa9577ac80136a74702f0e9f1973ebfc577`. Uploaded through the connected Fal plugin’s prepared-upload route and verified as 703,424 bytes before use. Source page: https://shuvfx.myportfolio.com/do-it-big.

- **room-v002:** source frame for style plus our complete A2 image for character. The edit added foreground leaves and light but largely retained the old side-on composition, outlined surfaces and flat room. Preserved, not recommended.
- **room-v003:** supplied only a crop of our character as the identity reference, then the original room frame as the principal scene reference. The crop is `(1400,170,2230,1080)` in A2’s 2752×1536 raster; no synthetic face editing. This removes most of the competing old-room composition from the conditioning. The prompt explicitly bases the new camera/framing and environment on the original frame.

The second attempt uses a frontal view, visible ceiling and room depth, foreground books/leaves, more numerous individually shaded plants, stronger window light and more textured bedding. The face, ponytail and violet clothing remain recognizable. The character and bedding retain visible contour lines; the result is closer in composition and lighting, not a complete reproduction of the original’s material richness. The small unicorn sketch is simpler than the original fine graphite drawing and needs its own close-up design before an insert shot.

The change involved reference cropping, ordering and prompt revision together. One pair of attempts cannot isolate which change caused the improvement.

## Review and next step

Recommend room-v003 as the new opening candidate. Inspect whether the richer setting and clearer depth resolve Olof’s main objection before building the angled pencil insert and galaxy scene. Foreground layers provide a plausible basis for parallax but do not prove a future video model will move them correctly.

Inspected the source frame, original A2, character crop, both returned image previews and the local room-v003 image. Both new outputs were downloaded, byte-counted and hashed; originals remain immutable. Generation returned 2752×1536 again, an approximation to the requested 16:9 ratio. Actual billing total was not returned.

## Records

- [room-v002 exact recipe and output](room-v002-receipt.json) · [file hash](room-v002-file.json)
- [room-v003 exact recipe and output](room-v003-receipt.json) · [file hash](room-v003-file.json)
- [Source/reference manifest](../references/manifest.json)
