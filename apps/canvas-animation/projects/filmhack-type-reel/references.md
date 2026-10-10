# Reference study

2026-10-10. Two local references supplied by Olof. Their SHA-256 values match the copies preserved by the [title-sequence study](../title-sequence-study/reference-source.json). Timestamps refer to the supplied files.

| Reference | File | Range studied |
|---|---|---|
| *Enter the Void* opening credits (ETV) | 141.0 s, 1280×544 (despite "1080p" in the name), 23.976 fps | 01:50–02:10 |
| *All Of The Lights* video (AOTL) | 327.7 s, 1280×720, 24 fps | 01:21–02:00 |

## What was inspected

- 4 fps overview sheets of both ranges.
- Every frame of five ETV windows; every second frame of four AOTL windows and every frame of AOTL 01:55.6–01:57.3.
- Spectrograms, RMS, low/mid band energy, onsets and beat tracking for both ranges (`tools/sound.py`, `tools/rhythm.py`).
- Frame-change classes (`tools/changes.py`). The replacement class is over-sensitive to internal animation; use it only as "how much of the image is changing".

Not possible: listening, perceiving normal-speed playback. AOTL windows sampled at 12 fps can hide single-frame events. Inspection sheets are local under `references/inspection/`.

## How each reference works

**ETV: relentless identity flux on a flat loop.** About 129 BPM with steady loudness and no drops in this range. Each name holds roughly 1–1.5 s and cycles through 8–12 designed identities of 1–4 frames each. Many identities appear as a bright frame followed by a dim one. Identity changes do not follow the beat. Almost every frame changes; the sequence works as texture rather than punctuation.

**AOTL: the arrangement decides the scale.** About 144 BPM. Before 01:35.9 the track is stripped back (held bass, no kick, about 8 dB quieter): one lyric word per card, timed to the vocal, mostly small dim outlines with black gaps. At 01:35.9 the beat drops and the picture goes full-frame: extruded 3D slabs, tunnels and giant cropped letters.

## Selected excerpts

| # | Source range | Contributes |
|---|---|---|
| 1 | ETV 01:51.03–01:52.57 | One name, about ten identities: slab, dot matrix, dots smeared into a radial tunnel, outline slab with script overlay, parallel-line inline, surname alone, star script, dotted script, katakana. Lettering variety and a 2–4-frame cadence with brightness pulses. |
| 2 | ETV 02:01.12–02:03.08 | Contours as motion: echo outlines multiply off the word, compress into stacked outlines and later expand into a concentric ring tunnel. The movement is the letter construction. |
| 3 | AOTL 01:33.80–01:38.55 | Sound and picture move together: tiny word in a void → glowing word → outline word slides in and blooms → letters echo as rings → neon word bursts into shards → about 0.3 s of near-black → tiny word → drop: full-frame extruded slabs, a tunnel, a giant cropped segmented word with RGB offset → small resolve. |
| 4 | AOTL 01:40.63–01:42.40 | Breath, then punch: about 1.1 s of a dim outline card that changes colour every frame, then giant flat white and blue words cropped by the frame edge, about four frames each, ending small. Editing and composition. |
| 5 | AOTL 01:43.60–01:44.45 | A sign builds itself: a thin outline word grows a marquee frame, stars, bulbs and arcs over about 0.4 s, overloads with glow and is cut away. Ornament and segments lighting up. |

Also useful: ETV 02:09.00–02:10.09 (the final name gets the biggest radial bloom, then resolves to a hairline outline) and AOTL 01:56.04–01:57.25 (a full-frame maze-lettered phrase, then single words reduced to geometric parts).

## Stills versus motion

The VEGAS sign (AOTL 01:46.85) and ETV's starry script (01:52.11) are beautiful stills that barely register as motion. The AOTL drop slabs (01:35.97–01:36.30) and ETV's vibrating contour noise (01:58.95–01:59.29) are poor stills but the most effective motion in either range.

## Implications for this Reel

- Pair a small quiet identity with an oversized loud one, and use the audio arrangement to decide when to be big (AOTL).
- Let important words pass through several designed identities within a second (ETV), while one stable motif keeps the reading anchored.
- Make motion out of the construction itself: contours expanding, segments lighting, signs assembling, slices separating.
- Photosensitivity: ETV alternates full-frame brightness up to about 12 Hz. Keep large-area flashes at or below three per second; confine faster flicker to small or low-contrast regions.
