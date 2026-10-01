import { AbsoluteFill } from "remotion";
import { DESIGN_WIDTH, FILM } from "../pixel/density";
import { PALETTE } from "../pixel/palette";
import { PixelCanvas } from "../pixel/PixelFrame";
import type { Pix } from "../pixel/pix";
import type { Vec2 } from "../pixel/shapes";
import { DURATION_SECONDS } from "../timing";
import { drawBoatScene } from "../stills/boatScene";
import {
  filmAt,
  panelFrame,
  panelNotation,
  SHEET_COLUMNS,
  SHOTS,
  shotSeconds,
  shotStart,
  type Shot,
} from "./shots";

const COLS = SHEET_COLUMNS;
// The score the shots are cut to.
const SCORE_VERSION = "v005";
const SCALE = 2;
const GAP = 36;
const MARGIN = 60;
const HEADER = 110;
const CAPTION = 200;
const PANEL_W = FILM.w * SCALE;
const PANEL_H = FILM.h * SCALE;
const ROWS = Math.ceil(SHOTS.length / COLS);
const DESIGN_HEIGHT = (DESIGN_WIDTH * FILM.h) / FILM.w;
// Notation is drawn in a warm red over the night scenes, edged in ink.
const NOTE = "#ff7a55";
const EDGE = PALETTE[0];

export const STORYBOARD_SIZE = {
  width: 2 * MARGIN + COLS * PANEL_W + (COLS - 1) * GAP,
  height: 2 * MARGIN + HEADER + ROWS * (PANEL_H + CAPTION) + (ROWS - 1) * GAP,
};

const clock = (s: number) => {
  const seconds = (s % 60).toFixed(1).padStart(4, "0").replace(/\.0$/, "");
  return `${Math.floor(s / 60)}:${seconds}`;
};

const arrowPaths = ([[ax, ay], [bx, by]]: readonly [Vec2, Vec2]) => {
  const len = Math.hypot(bx - ax, by - ay);
  const [dx, dy] = [(bx - ax) / len, (by - ay) / len];
  const [hx, hy] = [bx - dx * 7, by - dy * 7];
  return {
    shaft: `M ${ax} ${ay} L ${hx} ${hy}`,
    head: `M ${bx} ${by} L ${hx - dy * 4.5} ${hy + dx * 4.5} L ${hx + dy * 4.5} ${hy - dx * 4.5} Z`,
  };
};

// Arrows over a panel, in design-frame units.
const Notation: React.FC<{ shot: Shot }> = ({ shot }) => {
  const arrows = (panelNotation(shot).arrows ?? []).map(arrowPaths);
  if (!arrows.length) return null;
  const lines = arrows.map((a) => a.shaft).join(" ");
  const heads = arrows.map((a) => a.head).join(" ");
  return (
    <svg
      viewBox={`0 0 ${DESIGN_WIDTH} ${DESIGN_HEIGHT}`}
      width={PANEL_W}
      height={PANEL_H}
      style={{ position: "absolute", left: 0, top: 0 }}
    >
      <g strokeLinecap="round" strokeLinejoin="round">
        <path d={lines} fill="none" stroke={EDGE} strokeWidth={4.2} />
        <path d={heads} fill={EDGE} stroke={EDGE} strokeWidth={2.2} />
        <path d={lines} fill="none" stroke={NOTE} strokeWidth={2} />
        <path d={heads} fill={NOTE} stroke={NOTE} strokeWidth={0.6} />
      </g>
    </svg>
  );
};

const Panel: React.FC<{ shot: Shot }> = ({ shot }) => {
  const draw = (pix: Pix) =>
    drawBoatScene(pix, filmAt(panelFrame(shot)).spec, panelFrame(shot));
  const start = shotStart(shot);
  return (
    <div style={{ width: PANEL_W }}>
      <div style={{ position: "relative" }}>
        <PixelCanvas density={FILM} scale={SCALE} frame={0} draw={draw} />
        <Notation shot={shot} />
      </div>
      <div style={{ marginTop: 16, fontSize: 24, color: PALETTE[8] }}>
        {shot.id} · {clock(start)}–{clock(start + shotSeconds(shot))} ·{" "}
        {shot.framing}
      </div>
      <div style={{ marginTop: 6, fontSize: 30, color: PALETTE[11] }}>
        {shot.title}
      </div>
      <div
        style={{
          marginTop: 6,
          fontSize: 22,
          lineHeight: 1.3,
          color: PALETTE[9],
        }}
      >
        {shot.action}
      </div>
    </div>
  );
};

// The storyboard: one panel per shot, in order, with its time and action.
export const Storyboard: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: PALETTE[1],
      fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif",
      padding: MARGIN,
    }}
  >
    <div style={{ height: HEADER, fontSize: 44, color: PALETTE[10] }}>
      The Moon Fisher · storyboard · {SHOTS.length} shots cut to score{" "}
      {SCORE_VERSION}, {DURATION_SECONDS} s
    </div>
    <div
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${COLS}, ${PANEL_W}px)`,
        gridAutoRows: PANEL_H + CAPTION,
        gap: GAP,
      }}
    >
      {SHOTS.map((shot) => (
        <Panel key={shot.id} shot={shot} />
      ))}
    </div>
  </AbsoluteFill>
);
