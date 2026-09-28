import React from "react";
import {
  Composition,
  registerRoot,
  useCurrentFrame,
  AbsoluteFill,
} from "remotion";
function Shape({ kind }: { kind: "circle" | "sphere" | "ring" | "triangle" }) {
  const t = useCurrentFrame() / 15;
  const x = 280 + 460 * t,
    y = 205 - 45 * Math.sin(Math.PI * t),
    r = 74;
  return (
    <AbsoluteFill>
      <svg width={1024} height={576} viewBox="0 0 1024 576">
        <defs>
          <radialGradient id="shade" cx="30%" cy="25%" r="80%">
            <stop offset="0%" stopColor="#fff5d1" />
            <stop offset="65%" stopColor="#ddba70" />
            <stop offset="100%" stopColor="#6d532b" />
          </radialGradient>
        </defs>
        <g transform={`translate(${x},${y}) rotate(${t * 100})`}>
          {kind === "triangle" ? (
            <path d="M0 -85L78 55H-78Z" fill="#e3c990" />
          ) : kind === "ring" ? (
            <ellipse
              rx={r}
              ry={r * (0.4 + 0.6 * Math.abs(Math.cos(t * Math.PI)))}
              fill="none"
              stroke="#e3c990"
              strokeWidth={26}
            />
          ) : (
            <circle
              r={r}
              fill={kind === "sphere" ? "url(#shade)" : "#e3c990"}
            />
          )}
        </g>
      </svg>
    </AbsoluteFill>
  );
}
registerRoot(() => (
  <>
    {(["circle", "sphere", "ring", "triangle"] as const).map((kind) => (
      <Composition
        key={kind}
        id={`Inject-${kind}`}
        component={Shape}
        defaultProps={{ kind }}
        width={1024}
        height={576}
        durationInFrames={16}
        fps={4}
      />
    ))}
  </>
));
