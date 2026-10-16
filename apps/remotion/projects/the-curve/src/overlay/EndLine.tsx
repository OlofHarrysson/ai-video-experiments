import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { inter } from "../text/fonts";
import { smoothstep } from "../lib/math";

// The closing words, set quietly over the crowd: first the feeling, then the turn.
export const FEELING_IN = 36.5;
export const TURN_IN = 39.5;

const appear = (t: number, at: number) => smoothstep(at, at + 1.2, t);

export const EndLine: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const feeling = appear(t, FEELING_IN);
  const turnA = appear(t, TURN_IN);
  const turnB = appear(t, TURN_IN + 0.7);
  const out = 1 - smoothstep(43.6, 44.8, t);
  if (feeling <= 0) return null;
  const line: React.CSSProperties = {
    fontFamily: inter.fontFamily,
    color: "#eef1ff",
    letterSpacing: "0.32em",
    textTransform: "uppercase",
    textAlign: "left",
    whiteSpace: "nowrap",
    fontSize: 44,
  };
  const rise = (k: number) => `translateY(${(1 - k) * 10}px)`;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "flex-start", paddingLeft: 170, paddingBottom: 120 }}>
      <div style={{ ...line, fontWeight: 300, opacity: feeling * out, transform: rise(feeling) }}>Nobody can keep up.</div>
      <div style={{ ...line, fontWeight: 500, marginTop: 56, opacity: turnA * out, transform: rise(turnA) }}>
        This is the slowest
      </div>
      <div style={{ ...line, fontWeight: 500, marginTop: 16, opacity: turnB * out, transform: rise(turnB) }}>
        it will ever be.
      </div>
    </AbsoluteFill>
  );
};
