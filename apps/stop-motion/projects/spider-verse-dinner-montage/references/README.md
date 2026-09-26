# References

Film media stays in `assets/`, which Git ignores because this repository is public. [`extract_reference.py`](../scripts/extract_reference.py) creates the folder from a local copy of *Spider-Man: Across the Spider-Verse* (2023) and records that copy's path in `assets/SOURCE.txt`.

| File in `assets/` | Film time | Purpose |
| --- | --- | --- |
| `scene-context.mp4` | 3:44.0–4:10.0 | The whole dinner memory with sound: subway window, dinners, montage, school hallway |
| `montage.mp4` | 3:57.3–4:03.0 | The montage with a few frames of the shots on either side |
| `stills/image-01.png` … `image-63.png` | 3:57.571–4:02.742 | First frame of each montage image, 1920×800 |
| `montage-sheet.jpg` | 3:57.571–4:02.742 | All 63 images on one sheet |

Clips are H.264 CRF 18 with stereo AAC. Stills are 8-bit PNG frames decoded from a lossy source: references for composition, palette and timing, not clean artwork.

SHA-256 of the clips and sheet; `assets/SHA256SUMS` also covers every still:

- `scene-context.mp4`: `718b5f7f6730ad55a97cee1113ecda1938cfc03b11ed5397e386561c7a57ef2d`
- `montage.mp4`: `5ba4312b3293cec0b01f04efc6353518a24bfbfa13b8f3641706e249a782418f`
- `montage-sheet.jpg`: `8c72763bf6e4721a24f07b4ed27d75e07264aa386a310e9566e3f3de70131b5c`

[`montage-cadence.json`](montage-cadence.json) holds the measurement: each frame's colour swap and detailed motion values, each image's start time and length, and the summary shown in the [project README](../README.md#measured-timing).

To rebuild the folder, run from the project folder:

```sh
uv run --script scripts/extract_reference.py SOURCE_VIDEO
```

Timecodes refer to this copy; another release may be offset by a few frames.
