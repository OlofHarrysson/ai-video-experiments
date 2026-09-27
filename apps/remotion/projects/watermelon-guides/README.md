# Watermelon guides

A minimal Remotion SVG experiment for [the spatial-control lab](../../../comfyui/projects/spatial-control-lab/report.md). The circle moves from x=256 to x=768 over three seconds on a 1024-square canvas. Its radius stays 180. Seven frames, sampled every half second, are supplied to image models as placement guides.

```sh
npm ci
npm run guides
node scripts/render-comparison.mjs
```

The comparison command requires the lab's preserved round-three outputs. It renders a 3.5-second four-panel diagnostic: guide, independent Sunburst generations, Sunburst with a fixed watermelon reference, and Qwen 2.1 masked generation at a fixed seed. Each panel shows seven source images held at 2 fps in a 24 fps container. There are no synthesized intermediate images or motion interpolation. The separate `guide-motion.mp4` is the smooth SVG-only guide.

Outputs and manifests live in ignored `renders/v001/`. `comparison.mp4` was verified as 1024×1160, 84 frames, 24 fps, 3.5 seconds. All seven generated source frames per method were screened, along with rendered comparison frames and aligned rind crops. Source media remain owned by the spatial-control lab; copies under `public/` are disposable render inputs.
