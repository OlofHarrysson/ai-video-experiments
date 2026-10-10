# Lettering constraints and bounded fixes

| Observed problem | Effective fix in this experiment | Evidence needed |
| --- | --- | --- |
| Adjacent source panels overlap | One master image per identity; explicit safe-margin check | Three independently generated sources fit inside their image bounds |
| Trace rounds angular designs or retains raster stair steps | Per-asset spline/polygon mode and recorded simplification tolerance | Overlay and mask comparison; inspect corners and counters at full size |
| Trace loses delicate features | Source-versus-vector comparison and foreground-overlap measurement | Visual inspection remains decisive; overlap is not an aesthetic score |
| Vector paths are not semantic letters | Explicit named word/ornament groups with declared spatial regions or path IDs; reject missing/duplicate/ambiguous assignments | Every path belongs to one group; isolated word renders contain intact artwork |
| Animation pivots are implicit | Store bounds and editable normalized pivot per group | Inspector shows each group's bounds and pivot |
| WILD HOURS extraction is hardcoded | Shared manifest-driven extraction and inspection, project-owned source manifests | Process three different texts without modifying the shared tools |
| Silhouette cannot reproduce designed lighting | Keep optional separately traced detail layers; choose finishes suited to silhouettes for this board | Do not promise automatic material reconstruction |
| Strong stills do not guarantee good motion | Design a specific construction event for each identity; approve the sequence first | Later animation checkpoint compares local motion and the encoded edit |

## Deferred deliberately

- A reusable font or invented missing letters: new words get new master artwork.
- Automatic splitting of connected script into letters: the word is a useful controllable unit; manual separation is only justified by a specific shot.
- Automatic stroke write-on, arbitrary shape morphs and physically accurate 3D materials.
- A full asset-management or vector-editing UI. A small manifest and visual inspector are sufficient for this test.

Shared mechanics live in `apps/canvas-animation/tools/lettering/`; artwork, groups, prompts and the proposed story live here. Earlier studies remain immutable examples rather than dependencies to edit.
