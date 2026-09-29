import { useLayoutEffect, useRef } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { DESIGN_WIDTH, type Density } from "./density";
import { Pix } from "./pix";

// Draws a scene into a low-resolution canvas and scales it up with hard
// pixel edges.
export const PixelFrame: React.FC<{
  density: Density;
  draw: (pix: Pix, frame: number) => void;
}> = ({ density, draw }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const frame = useCurrentFrame();
  useLayoutEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const pix = new Pix(density.w, density.h, density.w / DESIGN_WIDTH);
    draw(pix, frame);
    const rgba = pix.toRGBA();
    const image = ctx.createImageData(density.w, density.h);
    image.data.set(rgba);
    ctx.putImageData(image, 0, 0);
  }, [density, draw, frame]);
  return (
    <AbsoluteFill style={{ backgroundColor: "#07080f" }}>
      <canvas
        ref={ref}
        width={density.w}
        height={density.h}
        style={{
          width: density.w * density.scale,
          height: density.h * density.scale,
          imageRendering: "pixelated",
        }}
      />
    </AbsoluteFill>
  );
};
