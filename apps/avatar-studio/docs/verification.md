# Verification — 30 September 2026

## Confirmed

- `npm run verify`: two Node input-boundary tests and Vite production build passed. Three.js produces a normal >500kB bundle-size warning; no build failure.
- Terminal Manager service `web` is ready at `http://localhost:3044/`; loopback binding confirmed in startup output. No unrelated service was changed.
- Browser inspected: live character rendered; Creative preset visibly changed skin, clothing, hair style and glasses.
- Dragging the canvas rotated the character into a side profile, confirming camera/geometry control. `evidence/rotated-character.jpg` captures that state. Browser console had no captured errors at final inspection.
- Importing a local WAV through the file chooser changed the active audio to the imported recording; the UI explicitly distinguishes it from the script text.
- Original Qwen sample decoded and played; a new script generated through the actual local `/api/speech` API, then played in the browser.
- Local speech endpoint returned valid 24kHz mono 16-bit WAV; inspected with `afinfo`.
- Live concurrency check held one streaming speech request open: a competing request returned 409, the original completed with 200, and a later request returned 200 after lock release.
- Export generated a 12.238-second performance with VP9 video and Opus audio. `ffprobe` verified video and audio streams; FFmpeg verified non-silent audio (mean -19.3 dB, peak -2.4 dB). A frame extracted from the actual recording showed an open talking mouth.
- The export API saved the result in `.private/exports/6d200836-6af5-42fe-b20e-f114678e872e.webm`. A local compatibility conversion is `.private/exports/demo.mp4` (H.264/AAC, approximately 1.3 MB).
- Desktop and 390px-width layout inspected. No horizontal page overflow observed at mobile width. Screenshots: `evidence/studio-desktop.jpg`, `evidence/studio-mobile.jpg`; exported frame: `evidence/performance-frame.jpg`.

## Changes driven by review

The in-app browser did not reliably expose Blob downloads to automation. Export now saves the actual file through the local API and offers a regular HTTP link. The saved bytes were inspected independently; a success label alone was not accepted as evidence.

Source review identified concurrent speech generation, delayed audio replacement, stale seek display and interrupted-export success-state issues. The speech lock is now owned per request; audio loading disables conflicting operations; progress continues after seeking; interrupted/failed recordings retain their failure state instead of being advertised as complete.

## Boundaries

- Lip-sync quality is visibly approximate and has not been human-rated by Olof. Audio energy controls mouth opening, not individual speech sounds.
- Voice likeness, face likeness and AI restyling are untested and unimplemented.
- Export is foreground real-time recording, not deterministic offline rendering. Backgrounding the tab interrupts the export with an explicit error.
- No cloud video model was run. Research compares documented features/prices, not measured provider output quality.
- Browser/API access worked without a new key. No secret was extracted from other projects.
- Learning from this trial: direct appearance control and generated talking video are different deliverables. The 3D pipeline proves control; next quality work should target the facial rig and lip-sync. No global instructions or memories were modified.
