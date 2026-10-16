import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { inter } from "../text/fonts";
import { smoothstep } from "../lib/math";

// The closing line, set quietly over the final image.
export const END_LINE_IN = 38;

export const EndLine: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const a = smoothstep(END_LINE_IN, END_LINE_IN + 1.2, t);
  const b = smoothstep(END_LINE_IN + 0.9, END_LINE_IN + 2.1, t);
  const out = 1 - smoothstep(43.6, 44.8, t);
  if (a <= 0) return null;
  const line: React.CSSProperties = {
    fontFamily: inter.fontFamily,
    color: "#eef1ff",
    letterSpacing: "0.32em",
    textTransform: "uppercase",
    textAlign: "left",
    whiteSpace: "nowrap",
  };
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "flex-start", paddingLeft: 170, paddingBottom: 120 }}>
      <div style={{ ...line, fontWeight: 300, fontSize: 46, opacity: a * out, transform: `translateY(${(1 - a) * 10}px)` }}>
        This is the slowest
      </div>
      <div style={{ ...line, fontWeight: 500, fontSize: 46, marginTop: 18, opacity: b * out, transform: `translateY(${(1 - b) * 10}px)` }}>
        it will ever be.
      </div>
    </AbsoluteFill>
  );
};
