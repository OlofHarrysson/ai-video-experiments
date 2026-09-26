import React from 'react';
import { AbsoluteFill, Interactive, random, useCurrentFrame } from 'remotion';
import { HOT, INK, PALETTE, WHITE, YELLOW } from '../brand';
import { Confetti, Sticker, Tape } from '../components/decor';
import { beatPulse, decayFrom, Shake, Slam } from '../components/motion';
import { FRAMES_PER_BEAT } from '../timing';

const SCREEN = { x: 60, y: 290, w: 960, h: 540 };

/** The film on the screen: the disco-ball moon from the prompts, over a skyline. */
const DiscoFilm: React.FC<{ readonly frame: number }> = ({ frame }) => {
  const cx = 640;
  const cy = 190;
  const r = 118;
  const facetShift = (frame * 3) % 28;
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', background: 'linear-gradient(#120a2e, #3a0f3a 70%, #5a1030)' }}>
      {Array.from({ length: 10 }, (_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: cx - 6,
            top: cy,
            width: 12,
            height: 900,
            transformOrigin: '50% 0',
            rotate: `${i * 36 + frame * 2.2}deg`,
            background: `linear-gradient(${PALETTE[i % PALETTE.length]}, transparent 70%)`,
            opacity: 0.35,
            mixBlendMode: 'screen',
          }}
        />
      ))}
      <div
        style={{
          position: 'absolute',
          left: cx - r,
          top: cy - r,
          width: 2 * r,
          height: 2 * r,
          borderRadius: '50%',
          backgroundColor: '#c9c9d6',
          backgroundImage:
            'linear-gradient(rgba(20,20,40,0.55) 3px, transparent 3px), linear-gradient(90deg, rgba(20,20,40,0.55) 3px, transparent 3px), radial-gradient(circle at 35% 30%, #ffffff, #9a9ab0 60%, #4a4a60)',
          backgroundSize: `28px 28px, 28px 28px, 100% 100%`,
          backgroundPosition: `${facetShift}px 0px, ${facetShift}px 0px, 0 0`,
          boxShadow: '0 0 60px 20px rgba(255,255,255,0.35)',
        }}
      />
      {Array.from({ length: 16 }, (_, i) => {
        const x = random(`sky-${i}`) * 960;
        const bh = 90 + random(`skyh-${i}`) * 180;
        return <div key={i} style={{ position: 'absolute', left: x - 40, bottom: 0, width: 80 + random(`skyw-${i}`) * 60, height: bh, backgroundColor: '#07040f' }} />;
      })}
    </div>
  );
};

const Audience: React.FC<{ readonly frame: number }> = ({ frame }) => {
  const bounce = beatPulse(frame, 4);
  return (
    <>
      {[
        { y: 1470, r: 44, n: 10 },
        { y: 1630, r: 58, n: 8 },
        { y: 1800, r: 76, n: 6 },
      ].map((row, ri) =>
        Array.from({ length: row.n }, (_, i) => {
          const seed = `${ri}-${i}`;
          const x = (i + 0.5 + (random(`ax-${seed}`) - 0.5) * 0.5) * (1080 / row.n);
          const armsUp = random(`arms-${seed}`) < 0.7;
          const jump = armsUp ? bounce * 18 * (0.6 + random(`j-${seed}`)) : 0;
          const phone = random(`phone-${seed}`) < 0.3;
          return (
            <div key={seed} style={{ position: 'absolute', left: x - row.r * 2, top: row.y - row.r - jump, width: row.r * 4, height: 600 }}>
              {armsUp ? (
                <>
                  <div style={{ position: 'absolute', left: row.r * 0.2, top: -row.r * 1.6, width: row.r * 0.5, height: row.r * 2.6, backgroundColor: INK, borderRadius: row.r, rotate: '-18deg', boxShadow: `0 -4px 0 ${HOT}` }} />
                  <div style={{ position: 'absolute', right: row.r * 0.2, top: -row.r * 1.6, width: row.r * 0.5, height: row.r * 2.6, backgroundColor: INK, borderRadius: row.r, rotate: '18deg', boxShadow: `0 -4px 0 ${HOT}` }} />
                  {phone ? <div style={{ position: 'absolute', right: -row.r * 0.1, top: -row.r * 2.3, width: row.r * 0.7, height: row.r * 1.15, backgroundColor: '#e8f0ff', border: `5px solid ${INK}`, borderRadius: 8 }} /> : null}
                </>
              ) : null}
              <div style={{ position: 'absolute', left: row.r, top: 0, width: row.r * 2, height: row.r * 2, borderRadius: '50%', backgroundColor: INK, boxShadow: `0 -5px 0 ${HOT}` }} />
              <div style={{ position: 'absolute', left: 0, top: row.r * 1.7, width: row.r * 4, height: 600, borderRadius: `${row.r * 2}px ${row.r * 2}px 0 0`, backgroundColor: INK, boxShadow: `0 -5px 0 ${HOT}` }} />
            </div>
          );
        }),
      )}
    </>
  );
};

/** Beats 32–40, drop two: the film premieres to a cheering full house. */
export const Premiere: React.FC = () => {
  const frame = useCurrentFrame();
  const sweep = Math.sin(frame / 7);
  return (
    <AbsoluteFill style={{ backgroundColor: '#07060A', overflow: 'hidden' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 30%, rgba(200,5,40,0.45), transparent 65%)' }} />
      <Shake amount={4 + 20 * decayFrom(frame, [0, 12, 24, 48])} seed="premiere">
        <div
          style={{
            position: 'absolute',
            left: SCREEN.x,
            top: SCREEN.y,
            width: SCREEN.w,
            height: SCREEN.h,
            border: `10px solid ${INK}`,
            boxShadow: '0 0 90px 30px rgba(255,255,255,0.18)',
            scale: String(1 + 0.03 * beatPulse(frame, 3)),
          }}
        >
          <DiscoFilm frame={frame} />
        </div>
        {[
          { x: 100, color: YELLOW, a: 26 * sweep },
          { x: 400, color: '#00D2E6', a: -18 * sweep },
          { x: 680, color: HOT, a: 18 * sweep },
          { x: 980, color: WHITE, a: -26 * sweep },
        ].map((beam) => (
          <div
            key={beam.x}
            style={{
              position: 'absolute',
              left: beam.x - 220,
              top: -200,
              width: 440,
              height: 2120,
              transformOrigin: '50% 100%',
              rotate: `${beam.a}deg`,
              background: `linear-gradient(to top, ${beam.color}, transparent 80%)`,
              clipPath: 'polygon(47% 100%, 53% 100%, 100% 0%, 0% 0%)',
              mixBlendMode: 'screen',
              opacity: 0.32,
            }}
          />
        ))}
        <Slam at={0} rotate={-4} style={{ left: 0, right: 0, top: 900, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div name="YOUR FILM" style={{ color: '#FFFFFF', fontFamily: 'MangoGrotesque', fontSize: 230, lineHeight: 1, filter: 'drop-shadow(12px 12px 0 #0A0A0A)' }}>
            YOUR FILM.
          </Interactive.Div>
        </Slam>
        <Slam at={12} rotate={3} style={{ left: 0, right: 0, top: 1120, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="ON THE BIG SCREEN tag"
            style={{
              backgroundColor: '#FFD400',
              color: '#0A0A0A',
              fontFamily: 'MangoGrotesque',
              fontSize: 118,
              lineHeight: 1,
              padding: '16px 36px 4px',
              border: '7px solid #0A0A0A',
              boxShadow: '12px 12px 0 #FF1E50',
            }}
          >
            ON THE BIG SCREEN!
          </Interactive.Div>
        </Slam>
        <Audience frame={frame} />
        {frame >= 48 ? <Tape y={860} angle={-4} speed={12} text="SUNDAY PREMIERE • REAL CINEMA • FULL HOUSE • " height={96} /> : null}
        <Sticker at={50} x={880} y={330} size={240} color="#00E08A" angle={14}>
          FULL
          <br />
          HOUSE!
        </Sticker>
        {Array.from({ length: 10 }, (_, i) => {
          const at = 12 + Math.floor(random(`flash-${i}`) * 80);
          const k = decayFrom(frame, [at], 2);
          if (k < 0.05) return null;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: 80 + random(`fx-${i}`) * 920 - 70,
                top: 1400 + random(`fy-${i}`) * 300 - 70,
                width: 140,
                height: 140,
                borderRadius: '50%',
                background: 'radial-gradient(circle, #ffffff 0%, rgba(255,255,255,0) 65%)',
                opacity: k,
              }}
            />
          );
        })}
        <Confetti at={0} x={80} y={1900} seed="cannon-l" direction={22} spread={40} power={3300} count={80} />
        <Confetti at={0} x={1000} y={1900} seed="cannon-r" direction={-22} spread={40} power={3300} count={80} />
        <Confetti at={FRAMES_PER_BEAT * 4} x={540} y={1950} seed="cannon-c" direction={0} spread={70} power={3600} count={100} />
      </Shake>
    </AbsoluteFill>
  );
};
