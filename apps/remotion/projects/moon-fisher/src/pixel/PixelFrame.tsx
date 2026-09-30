import { useLayoutEffect, useRef } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { DESIGN_WIDTH, type Density } from "./density";
import { Pix } from "./pix";

// A scene drawn into a low-resolution canvas and enlarged `scale` times with
// hard pixel edges.
export const PixelCanvas: React.FC<{
  density: Density;
  scale: number;
  frame: number;
  draw: (pix: Pix, frame: number) => void;
}> = ({ density, scale, frame, draw }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const pix = new Pix(density.w, density.h, density.w / DESIGN_WIDTH);
    draw(pix, frame);
    const image = ctx.createImageData(density.w, density.h);
    image.data.set(pix.toRGBA());
    ctx.putImageData(image, 0, 0);
  }, [density, draw, frame]);
  return (
    <canvas
      ref={ref}
      width={density.w}
      height={density.h}
      style={{
        display: "block",
        width: density.w * scale,
        height: density.h * scale,
        imageRendering: "pixelated",
      }}
    />
  );
};

// A full frame of the film at the current frame.
export const PixelFrame: React.FC<{
  density: Density;
  draw: (pix: Pix, frame: number) => void;
}> = ({ density, draw }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#07080f" }}>
      <PixelCanvas
        density={density}
        scale={density.scale}
        frame={frame}
        draw={draw}
      />
    </AbsoluteFill>
  );
};
