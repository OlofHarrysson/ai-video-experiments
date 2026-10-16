import { ThreeCanvas } from "@remotion/three";
import { useEffect, useState } from "react";
import { AbsoluteFill, cancelRender, continueRender, delayRender, useCurrentFrame, useVideoConfig } from "remotion";
import { World } from "./World";
import { EndLine } from "./overlay/EndLine";
import { PALETTE } from "./palette";
import { Atlas, buildAtlas } from "./text/atlas";
import { fontsReady } from "./text/fonts";
import { smoothstep } from "./lib/math";
import { ACT } from "./timing";

// Out of black at the start, back to black at the end.
const Fade: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;
  const end = durationInFrames / fps;
  const black = Math.max(1 - smoothstep(0, 1.2, t), smoothstep(end - 1.2, end - 0.1, t));
  // One white flash on the reveal's downbeat.
  const flash = t >= ACT.reveal[0] && t < ACT.reveal[0] + 0.5 ? 0.7 * Math.exp(-(t - ACT.reveal[0]) * 14) : 0;
  return (
    <>
      {flash > 0.01 ? <AbsoluteFill style={{ backgroundColor: "#f4f6ff", opacity: flash }} /> : null}
      {black > 0 ? <AbsoluteFill style={{ backgroundColor: "black", opacity: black }} /> : null}
    </>
  );
};

export const TheCurve: React.FC = () => {
  const { width, height } = useVideoConfig();
  const [atlas, setAtlas] = useState<Atlas | null>(null);
  const [handle] = useState(() => delayRender("Loading fonts and drawing the text atlas"));

  useEffect(() => {
    fontsReady()
      .then(() => setAtlas(buildAtlas()))
      .catch((err) => cancelRender(err));
  }, []);

  // Released after the canvas has mounted (and taken its own hold), so no frame slips through
  // before the world exists.
  useEffect(() => {
    if (atlas) continueRender(handle);
  }, [atlas, handle]);

  return (
    <AbsoluteFill style={{ backgroundColor: PALETTE.zenith }}>
      {atlas ? (
        <ThreeCanvas
          width={width}
          height={height}
          dpr={1}
          flat
          gl={{ antialias: false, alpha: false, powerPreference: "high-performance", stencil: false }}
          camera={{ fov: 38, near: 0.05, far: 20000, position: [0, 1.5, 4] }}
        >
          <World atlas={atlas} />
        </ThreeCanvas>
      ) : null}
      <EndLine />
      <Fade />
    </AbsoluteFill>
  );
};
