import { AbsoluteFill } from "remotion";
import { FILM } from "../pixel/density";
import { PALETTE } from "../pixel/palette";
import { PixelCanvas } from "../pixel/PixelFrame";
import type { Pix } from "../pixel/pix";
import { drawBoatScene } from "../stills/boatScene";
import { FPS } from "../timing";
import { SHOTS, shotSeconds, shotStart, type Shot } from "./shots";

const COLS = 6;
const SCALE = 2;
const GAP = 36;
const MARGIN = 60;
const HEADER = 110;
const CAPTION = 200;
const PANEL_W = FILM.w * SCALE;
const PANEL_H = FILM.h * SCALE;
const ROWS = Math.ceil(SHOTS.length / COLS);

export const STORYBOARD_SIZE = {
  width: 2 * MARGIN + COLS * PANEL_W + (COLS - 1) * GAP,
  height: 2 * MARGIN + HEADER + ROWS * (PANEL_H + CAPTION) + (ROWS - 1) * GAP,
};

const clock = (s: number) => {
  const seconds = (s % 60).toFixed(1).padStart(4, "0").replace(/\.0$/, "");
  return `${Math.floor(s / 60)}:${seconds}`;
};

const Panel: React.FC<{ shot: Shot }> = ({ shot }) => {
  const draw = (pix: Pix) =>
    drawBoatScene(pix, shot.spec(shot.panel), Math.round(shot.panel * FPS));
  const start = shotStart(shot);
  return (
    <div style={{ width: PANEL_W }}>
      <PixelCanvas density={FILM} scale={SCALE} frame={0} draw={draw} />
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
      The Moon Fisher · storyboard · {SHOTS.length} shots cut to score v003, 60
      s
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
