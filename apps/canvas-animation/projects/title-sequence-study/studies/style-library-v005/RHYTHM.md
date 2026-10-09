# Medium to medium-high timing experiment

2026-10-09. Olof finds the original opening too slow and the ultra-fast ending somewhat too fast. He prefers medium to medium-high intensity, with a little rhythm and no requirement for a clear linear escalation. This revision changes timing and ordering; the artwork and original edit remain preserved.

[Current 24-second cut](output-rhythm-medium-high/showcase.mp4) · [Review page with original comparison](review.html)

- Immediate full-size neon movement; no quiet tiny-word prelude or long black release.
- A 120 BPM visual grid: 12 two-second bars. Holds are either 12 frames / 0.5 seconds or 6 frames / 0.25 seconds at 24 fps. There are no two- or four-frame shots.
- The first half has 27 holds; the second has 36. This makes a modest lift from 2.25 to 3 treatments per second on average. It is an editing hypothesis, not a measurement of perceived intensity.
- Returning script, marquee and serif motifs create a refrain. Flat print, outlines and denser layouts interrupt those returns, rather than every successive shot getting faster.
- Consecutive treatments of the same identity share a continuous local motion clock, so material edits do not repeatedly restart their native movement.
- Silent, as before. The BPM is an editing pulse, not a selected soundtrack or a claim about musical synchronization.

`cut-rhythm.js` owns the new sequence. `cut.js` still owns the original escalation. Render to a new destination:

```sh
CUT_FILE=cut-rhythm.js OUTPUT=output-rhythm-medium-high node render-cut.mjs
```

This destination already exists on the working checkout; use another name for another run. The renderer retains source snapshots, a timeline, source hashes and a contact sheet.

Validation: all 576 frames decode at 1280×720 / 24 fps, duration 24 seconds, no audio and no black frames. There are 63 holds: 33 half-second holds and 30 quarter-second holds. Same-frame hashes remain repeatable after out-of-order seeking; no browser errors. The review page loads and seeks all five videos, including the preserved comparison.

Assistant inspected the encoded overview plus every frame in 0.875–1.375 seconds and 20.375–20.875 seconds. Those windows confirm registered treatment changes and internal motion within the longer holds. Normal-speed feel remains for Olof to judge. Verification receipt: `output-rhythm-medium-high/verification.json`; SHA-256 `69edc29c24b0771c5af6e71812e747cb7bd9d7a156d6ed819d0d9b638f1c73ef`.

The initial sprint's `release.json` remains a record of its four original exports. This timing experiment is documented separately so those earlier results retain their provenance.
