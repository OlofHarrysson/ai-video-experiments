import { useThree } from "@react-three/fiber";
import { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Vector2, Vector3 } from "three";
import { Shot, cameraAt, chaos } from "./camera";
import { campusGlows, headlineCards, launchGlows, launchTags, nowMarker, tickLabels } from "./content";
import { endCamera } from "./ending";
import { revealCamera, revealMapping } from "./reveal";
import { IDENTITY, Mapping, leaderS, racerHead } from "./race";
import { Atlas } from "./text/atlas";
import { ACT, worldClock } from "./timing";
import { CameraRig } from "./world/CameraRig";
import { Crowd } from "./world/Crowd";
import { DataCenters } from "./world/DataCenters";
import { Figure } from "./world/Figure";
import { Glow, Glows } from "./world/Glows";
import { GuideLines, Stroke } from "./world/GuideLines";
import { Ground } from "./world/Ground";
import { Label, Labels } from "./world/Labels";
import { Post } from "./world/Post";
import { Racers, activeRacers, headPosition, racerColor } from "./world/Racers";
import { Sky } from "./world/Sky";
import { keys, smoothstep } from "./lib/math";

const HERO: [number, number, number] = [-0.45, 0, 0];

/** The ending's chart: a whole race squeezed into a floor line and a column. */
export const END_MAP: Mapping = { sx: 0.27, sy: 0.05, sl: 0.13, x0: 3 };
const END_FOCUS = new Vector3(END_MAP.x0, 0, -30);
/** The ending draws the race up to here: the column already rises far out of frame. */
const END_S_MAX = 165;
const END_LIGHT = new Vector3(END_MAP.x0, 40, -30);
const RACE_LIGHT = new Vector3(0, 2.5, -60);

const headGlows = (w: number, m: Mapping, out: Glow[], scale = 1, sMax = Infinity) => {
  for (const racer of activeRacers(w)) {
    if (racerHead(racer, w) > sMax) continue;
    const age = w - racer.spawn;
    const flash = racer.id === 0 ? 0 : Math.exp(-Math.max(0, age) * 3) * 3;
    const ignite = racer.id === 0 ? smoothstep(0.2, 1.4, w) : 1;
    out.push({
      position: headPosition(racer, w, m),
      color: racerColor(racer),
      px: 7,
      world: 0.4 * scale,
      intensity: (1.1 + flash) * ignite,
      streak: 2.6,
    });
  }
};

const useResolution = () => {
  const gl = useThree((s) => s.gl);
  const resolution = useMemo(() => new Vector2(), []);
  gl.getDrawingBufferSize(resolution);
  return resolution;
};

const RaceWorld: React.FC<{ t: number; atlas: Atlas }> = ({ t, atlas }) => {
  const resolution = useResolution();
  const w = worldClock(t);
  const revealing = t >= ACT.reveal[0];
  const shot: Shot = revealing ? revealCamera(t) : cameraAt(t);
  const m = revealing ? revealMapping(t) : IDENTITY;
  const near = revealing ? Math.max(0.05, shot.position.length() * 0.002) : 0.05;
  const c = chaos(t);
  // Into the reveal: the storm clears, and only NOW stays on the chart.
  const clear = 1 - smoothstep(ACT.reveal[0], ACT.reveal[0] + 0.5, t);
  const hit = revealing ? Math.exp(-(t - ACT.reveal[0]) * 5) : 0;

  const glows: Glow[] = [];
  const tags: Label[] = [];
  const ticks: Label[] = [];
  const cards: Label[] = [];
  campusGlows(w, m, glows);
  launchGlows(w, m, glows);
  headGlows(w, m, glows);
  tickLabels(w, m, glows, ticks, clear);
  launchTags(w, m, tags, clear);
  headlineCards(w, m, cards, clear);
  const strokes: Stroke[] = [];
  if (revealing) nowMarker(m, smoothstep(ACT.reveal[0] + 0.6, ACT.reveal[0] + 1.2, t), strokes);

  const fog = revealing ? 2500 : keys(w, [[0, 70], [12, 100], [17, 220], [21, 600], [24, 900]]);
  return (
    <>
      <CameraRig shot={shot} near={near} far={40000} />
      <Sky cam={shot.position} radius={18000} />
      <Ground
        cam={shot.position}
        headS={leaderS(w)}
        fogDist={fog}
        scale={revealing ? 10 : 1}
        sx={m.sx}
        sy={m.sy}
      />
      <DataCenters t={w} cam={shot.position} fogDist={fog * 1.3} mapping={m} />
      {t < 9 ? <Figure cam={shot.position} light={RACE_LIGHT} position={HERO} /> : null}
      <Racers w={w} cam={shot.position} mapping={m} resolution={resolution} near={near} />
      <Glows glows={glows} resolution={resolution} near={near} capacity={8192} />
      <GuideLines strokes={strokes} resolution={resolution} near={near} />
      <Labels atlas={atlas} labels={[...ticks, ...tags]} resolution={resolution} near={near} additive />
      <Labels atlas={atlas} labels={cards} resolution={resolution} near={near} />
      <Post
        bloom={1.1 + c * 0.6 + hit * 2.5}
        aberration={c * 0.0025 + hit * 0.006}
        vignette={0.55 + c * 0.2}
      />
    </>
  );
};

const EndWorld: React.FC<{ t: number }> = ({ t }) => {
  const resolution = useResolution();
  const w = worldClock(t);
  const shot = endCamera(t);
  const near = 0.05;
  const m = END_MAP;
  const glows: Glow[] = [];
  launchGlows(w, m, glows, END_S_MAX);
  headGlows(w, m, glows, 3, END_S_MAX);
  const crowd = smoothstep(ACT.end[0] + 2.5, ACT.end[0] + 6, t);
  return (
    <>
      <CameraRig shot={shot} near={near} far={20000} />
      <Sky cam={shot.position} dawn={1.6} />
      <Ground cam={shot.position} headS={leaderS(w)} fogDist={110} sx={m.sx} sy={m.sy} poolStrength={0.5} poolWidth={1.2} />
      <Figure cam={shot.position} light={END_LIGHT} position={HERO} lookUp={1} rim={2.2} />
      <Crowd cam={shot.position} light={END_LIGHT} focus={END_FOCUS} reveal={0.4 + 0.6 * crowd} />
      <Racers w={w} cam={shot.position} mapping={m} resolution={resolution} near={near} intensity={1.4} worldWidth={0.3} sMax={END_S_MAX} />
      <Glows glows={glows} resolution={resolution} near={near} />
      <Post bloom={1.35} vignette={0.65} />
    </>
  );
};

export const World: React.FC<{ atlas: Atlas }> = ({ atlas }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return t >= ACT.end[0] ? <EndWorld t={t} /> : <RaceWorld t={t} atlas={atlas} />;
};
