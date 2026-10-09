# Surface material study

`surface.js` shades a cached 2D lettering mask using a bevel-height approximation and an analytic reflection palette. It does not create a 3D mesh and is not physically based rendering. The original artwork remains deterministic.

The Euclidean distance transform uses a separable lower-envelope implementation informed by Algorithm 1 and section 2.2 of Pedro F. Felzenszwalb and Daniel P. Huttenlocher, *Distance Transforms of Sampled Functions*, Theory of Computing 8 (2012), 415–428. [Author-hosted paper](https://cs.brown.edu/people/pfelzens/papers/dt-final.pdf). The JavaScript implementation here was written for this study; no external implementation or dependency was copied.

First renders used a chamfer approximation. That produced visible ribs and unstable small reflection bands. Replacing it with Euclidean distances and smoothing the field reduces grid artifacts. The initial bevel radius was also wider than the letter strokes, leaving a discontinuity at their middle; fitting the radius to the stroke thickness is part of the correction. Preserve the first attempts as evidence, not preferred artwork.

The material engine can accept another mask; the current study only establishes it on the custom rounded skeleton alphabet. It is not validated on arbitrary thin fonts or different resolutions. Field and frame caches are bounded; render frame parameters explicitly rather than depending on playback history.
