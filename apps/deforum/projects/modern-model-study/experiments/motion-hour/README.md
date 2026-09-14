# One hour of stronger spatial motion

Olof finds the previous two films quite nice but too static. He wants more readable panning, zooming and spatial warping. This extension runs from approximately 18:22:32 to 19:22:32 UTC on 2026-09-14. Finish already-started work afterward if necessary; keep this extension plus the preceding session within $10 total. Preserve all attempts and the recurrent Krea feedback loop. Final deliveries remain 24 fps with RIFE; preview the underlying motion before repainting.

## First round

Reuse Porcelain Weather's exact opening, prompt stages, noise curve, painting times, seeds and three-interval Euler/CFG1 recipe. Restart from frame zero, changing only the motion path. Each fourteen-second branch has 27 new paintings.

- Sweeping camera: substantially larger zooms and pans, with broad turns and changes of direction. Positive zoom creates some room for panning; it does not guarantee artifact-free borders.
- Travelling twist: stronger localized turns around changing centres, alternating direction so the whole scene does not wind up around one point indefinitely.

The existing fourteen-second stronger-transformation version is the historical baseline. Inspect direct motion previews and recurrent raw paintings separately. Large movement may expose reflected borders, make RIFE struggle or be partly undone by repainting. Measure/observe those effects before interpreting the outcome as a motion-control success. The shared runner is reused through an explicit experiment path adapter; no diffusion graph or dependency change is intended.

## Travelling wave control

A third matched branch adds an invertible horizontal shear wave: x displacement varies sinusoidally with y and time, while y is unchanged. A smooth envelope brings it back to zero at either end of each phrase. It combines opposite movement in different image bands with a mild zoom and pan. This is direct mathematical motion; no optical-flow or depth model is added. Forward/inverse tests include composition with the existing twist/zoom transform and exact identity outside the wave interval. All historical motion paths retain their existing branch. Preview the motion before submitting this branch.

Motion-only review: the camera branch has substantially closer framing and a tilting horizon, while the strong twist carries the wave upward and leaves more empty space late. Keep that as an explicit deformation stress case. The travelling wave bends the wave face and slides image bands back and forth while broadly retaining the initial framing; no major empty border was visible in the sampled preview. These previews sample the original image through the cumulative mapping at each time, rather than applying repeated image resampling or diffusion.
