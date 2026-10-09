# Motion tooling and study

## Authorized outcome

2026-10-09: Olof requests the tooling improvements and accepts a study of six to eight different motion behaviors followed by an escalating montage. GSAP is preferred based on previous experience. Theme remains open. This is an explicitly authorized motion experiment before a film storyboard.

The first typography study is decent but less impressive than the reference. Olof likes the neon identity but finds its motion nearly absent; the detached flourish under the script feels out of place. He likes the more active tangled outlines and accepts simpler treatments among complex ones. The target is a large variety of identities and movements, not one unified look. His numbering appears to refer to the four shots in the motion reel.

## This sprint

1. Project-local, pinned GSAP and OpenType.js dependencies; no global installation or changes to the vendored Animate skill.
2. Seekable GSAP choreography, font-outline extraction, point deformation, reusable masks and deterministic particle positions.
3. Eight motion studies: neon construction/breakup, particle assembly, deforming blackletter, individual letter choreography, contour vortex, slicing/shearing, RGB separation and typographic collisions.
4. A labeled catalogue for reviewing individual behaviors and a short montage with progressively shorter holds and more internal motion. Silent to isolate visual motion; sound escalation remains a separate experiment.
5. Inspect rendered samples and transition windows; verify arbitrary-time seeking gives repeatable frames and each scene has substantial visible changes. Preserve previous study.

## Deferred ideas, with concrete triggers

- GPU/WebGL effects: add only when a selected treatment needs fluid displacement, feedback trails, bloom or perspective that Canvas cannot render economically. Prototype one effect before choosing a shared GPU stack.
- More type: collect licensed display faces with contrasting construction (condensed, grotesque, rounded, blackletter, script, multilingual). Start with a small OFL set and retain provenance/licenses. Font quantity alone is not design variety.
- Custom lettering: design word-specific ligatures and integrated ornaments. Replace detached decorative flourishes. True glyph-to-glyph morphing requires contour matching; outline warping does not prove morphing.
- Sound: define a rising density/energy curve, then test cuts and internal accents against percussion, noise and sustained tones. No final soundtrack or claims about audible quality yet.
- Final film: select an accessible theme with Olof after motion review; AI progress/investment/hype is one candidate. Verify factual claims if used.
- Portability: replace remaining local Mac-font dependencies if a distributable browser piece is chosen. MP4 export does not depend on recipient fonts.

## Continuation

The first motion sprint is complete. Olof found it better but identified plain graphic design as the primary risk. Three focused identities followed in `studies/design-v003/`. He prefers Night Fever as a still and rejects its movement. Claude login was restored and an Opus 5.5 consultation completed; the saved critique informed `studies/motion-v004/`, a fixed-composition material cycle tested at three speeds. Read that study's README and artifacts before further changes. Preserve the Night Fever artwork, and wait for Olof's playback judgment before treating this new motion as successful. The final film still needs many different identities and a selected theme.

Read this plan, the project README, and the latest study README for current evidence and remaining work. Keep reusable primitives in project-owned `tools/`; promote to workspace tooling only after a second project needs them.
