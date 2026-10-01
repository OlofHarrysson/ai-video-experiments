import { AbsoluteFill, useCurrentFrame } from "remotion";
import { PALETTE } from "./pixel/palette";
import { at, BAR_SECONDS, BARS, FPS, SECTIONS, type Section } from "./timing";

// What happens in the story during each passage of the score.
const STORY: Record<Section, string> = {
  intro: "Night sea. The float bobs beside the moon's reflection.",
  tune: "The clarinet's tune over the piano. Nothing bites; he nods off.",
  doze: "He sleeps, and the moon drifts into his hook.",
  tug: "A tug on the line: the float twitches, then plunges.",
  hooked: "The moon is hooked. A held breath; he sleeps on.",
  haul: "He wakes and hauls the moon down the sky.",
  catch: "The moon comes out of the water. The sky goes dark.",
  wonder: "The moon in his bucket lights his face.",
  dimming: "It starts to fade, like a fish out of water.",
  release: "He tips it back into the sea.",
  darkness: "A held beat of darkness.",
  rise: "The sea brightens from below; the moon rises.",
  finale: "Home in a new key. Fish leap; one lands; the cat gets it.",
  coda: "The last shot mirrors the first.",
};

const mmss = (s: number) =>
  `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

// A review aid for the score: the passages of the story, with the one
// playing now lit up.
export const ScoreMap: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const bar = Math.min(BARS, Math.floor(t / BAR_SECONDS) + 1);
  const entries = Object.entries(SECTIONS) as [
    Section,
    readonly [number, number],
  ][];
  const current =
    entries.find(([, [a, z]]) => bar >= a && bar < z)?.[0] ?? "coda";
  return (
    <AbsoluteFill
      style={{
        backgroundColor: PALETTE[1],
        color: PALETTE[9],
        fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif",
        padding: "120px 90px",
      }}
    >
      <div style={{ fontSize: 40, opacity: 0.7 }}>The Moon Fisher · score</div>
      <div style={{ fontSize: 34, opacity: 0.55, marginTop: 12 }}>
        bar {bar} of {BARS} · {mmss(t)}
      </div>
      <div
        style={{
          marginTop: 70,
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        {entries.map(([name, [a, z]]) => {
          const active = name === current;
          const done = at(z) <= t;
          const progress = Math.min(
            1,
            Math.max(0, (t - at(a)) / (at(z) - at(a))),
          );
          return (
            <div
              key={name}
              style={{
                position: "relative",
                padding: "20px 26px",
                borderRadius: 14,
                backgroundColor: active ? PALETTE[4] : PALETTE[2],
                opacity: active ? 1 : done ? 0.45 : 0.7,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  width: `${progress * 100}%`,
                  backgroundColor: active ? PALETTE[5] : "transparent",
                }}
              />
              <div
                style={{
                  position: "relative",
                  display: "flex",
                  gap: 22,
                  alignItems: "baseline",
                }}
              >
                <span style={{ fontSize: 30, width: 170, color: PALETTE[8] }}>
                  {mmss(at(a))}–{mmss(at(z))}
                </span>
                <span
                  style={{
                    fontSize: active ? 44 : 36,
                    color: active ? PALETTE[11] : PALETTE[9],
                  }}
                >
                  {name}
                </span>
              </div>
              {active ? (
                <div
                  style={{
                    position: "relative",
                    fontSize: 34,
                    marginTop: 10,
                    color: PALETTE[10],
                    lineHeight: 1.3,
                  }}
                >
                  {STORY[name]}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
