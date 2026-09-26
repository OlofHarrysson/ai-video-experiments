import React from 'react';
import { AbsoluteFill, Interactive, random, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { MONO, PALETTE, SEG, YELLOW } from '../brand';
import { Halftone } from '../components/decor';
import { PersonIcon } from '../components/icons';
import { decayFrom, Shake, Slam } from '../components/motion';

const CELL = 84;
const LEFT = (1080 - CELL * 10) / 2;
const TOP = 560;

/** Pop-in frame for each of the 100 creators, in a shuffled order that speeds up. */
const APPEAR = (() => {
  const order = Array.from({ length: 100 }, (_, i) => i).sort((a, b) => random(`crowd-${a}`) - random(`crowd-${b}`));
  const at = new Array<number>(100);
  order.forEach((cell, rank) => {
    at[cell] = 2 + 26 * Math.pow(rank / 99, 0.75);
  });
  return at;
})();

/** Beats 20–24: a hundred creators pop into the grid while the counter runs to 100. */
export const Crowd: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const count = APPEAR.filter((a) => a <= frame).length;
  return (
    <AbsoluteFill style={{ backgroundColor: '#0A0A0A', overflow: 'hidden' }}>
      <Halftone color="rgba(0,210,230,0.12)" />
      <Shake amount={3 + 20 * decayFrom(frame, [24, 36])} seed="crowd">
        <div style={{ position: 'absolute', left: 0, right: 0, top: 230, textAlign: 'center', fontFamily: SEG, fontSize: 190, lineHeight: 1, textShadow: 'none' }}>
          <span style={{ position: 'absolute', left: 0, right: 0, color: 'rgba(255,212,0,0.1)' }}>888</span>
          <span style={{ position: 'relative', color: YELLOW, textShadow: `0 0 30px ${YELLOW}` }}>{String(count).padStart(3, '0')}</span>
        </div>
        <div style={{ position: 'absolute', left: 0, right: 0, top: 450, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 36, letterSpacing: 8, color: 'rgba(255,255,255,0.75)' }}>
          CREATORS · ONE WEEKEND
        </div>
        {APPEAR.map((at, i) => {
          const pop = spring({ frame: frame - at, fps, config: { damping: 10, stiffness: 260, mass: 0.4 } });
          if (frame < at) return null;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: LEFT + (i % 10) * CELL + 4,
                top: TOP + Math.floor(i / 10) * CELL + 4,
                scale: String(pop),
                rotate: `${(random(`tilt-${i}`) - 0.5) * 20}deg`,
              }}
            >
              <PersonIcon size={CELL - 8} color={PALETTE[Math.floor(random(`color-${i}`) * PALETTE.length)]} />
            </div>
          );
        })}
        <Slam at={24} rotate={-5} style={{ left: 0, right: 0, top: 700, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="100 CREATORS tag"
            style={{
              backgroundColor: '#C80528',
              color: '#FFFFFF',
              fontFamily: 'MangoGrotesque',
              fontSize: 200,
              lineHeight: 1,
              padding: '20px 40px 6px',
              border: '7px solid #0A0A0A',
              boxShadow: '14px 14px 0 #FFD400',
            }}
          >
            100 CREATORS
          </Interactive.Div>
        </Slam>
        <Slam at={36} rotate={4} style={{ left: 0, right: 0, top: 1010, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="30+ TEAMS tag"
            style={{
              backgroundColor: '#FFD400',
              color: '#0A0A0A',
              fontFamily: 'MangoGrotesque',
              fontSize: 200,
              lineHeight: 1,
              padding: '20px 40px 6px',
              border: '7px solid #0A0A0A',
              boxShadow: '14px 14px 0 #00D2E6',
            }}
          >
            30+ TEAMS
          </Interactive.Div>
        </Slam>
      </Shake>
    </AbsoluteFill>
  );
};
