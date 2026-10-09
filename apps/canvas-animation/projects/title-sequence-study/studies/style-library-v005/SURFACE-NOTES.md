# Surface material study

`surface.js` approximates a rounded lettering surface in Canvas 2D. It does not create a mesh, simulate lighting physically or provide depth ordering at crossings. All frames are deterministic.

## Two field sources

- **Generic uppercase masks:** an exact Euclidean distance transform measures the distance to background pixels. Three small smoothing passes reduce grid-shaped reflection ribs. The transform uses a separable lower-envelope implementation informed by Algorithm 1 and section 2.2 of Pedro F. Felzenszwalb and Daniel P. Huttenlocher, *Distance Transforms of Sampled Functions*, Theory of Computing 8 (2012), 415–428. [Author-hosted paper](https://cs.brown.edu/people/pfelzens/papers/dt-final.pdf). This study's JavaScript implementation was written locally; no external implementation or package was copied.
- **Original Wild path:** the cubic centreline is sampled at one-pixel arc-length intervals. Spatial bins find the nearest line segment and its analytic normal, avoiding bitmap-distance quantization. A small smooth union blends distant intersecting branches. Nearby samples on the same stroke are excluded from that blend so a straight stem does not acquire a seam from its own neighbours.

The shader combines a rounded cross-section, a simple diffuse/specular resin material, hard reflection palettes and an interference pattern. Reflection phases advance on fours. Resin is deliberately quiet within one state. Bounded caches store fields and a small number of rendered material frames.

## Evidence and limits

The first chamfer-based version produced strong ribs. Exact distances, appropriate bevel radius, smoothing and then analytic path normals progressively improved it. All attempts remain in versioned local output directories. Rose resin is the most reliable current finish. Silver/gold expose small contour irregularities and intersection pinches; their fused crossings are not a physically correct over/under weave. Generic uppercase lettering still relies on raster masks and may show stronger bands. A final wider-union trial was rejected because it made the joins swollen and introduced additional ridges; its output and source snapshot remain under `output-surface-wide-union/`. The selected source restores the narrower union.

`check-surface.mjs` compares the Euclidean transform against an independent brute-force oracle on 18 small masks / 1,489 pixels. Maximum observed error was 2.42e-8. This verifies distances, not the artistic result or the lighting model. Full-size stills and encoded-frame windows were also inspected.

The material engine is currently tested at 1280×720 on the study's lettering. Thin arbitrary fonts, a different resolution, physical reflections and a generalized 3D extrusion pipeline remain unproved. Before using a reflective word as a prolonged hero shot, resolve its actual crossings and inspect motion at delivery size.
