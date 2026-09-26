import React from 'react';
import { AbsoluteFill, Interactive, useCurrentFrame } from 'remotion';
import { Confetti, Halftone, Rays, Sticker, Tape } from '../components/decor';
import { WarningIcon } from '../components/icons';
import { decayFrom, Punch, Shake, Slam } from '../components/motion';

const HITS = [0, 12, 24, 36];

/** Beats 0–4: a ransom-note stack, one word per beat, over a siren. */
export const ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: '#0A0A0A', overflow: 'hidden' }}>
      <Rays colors={['#0A0A0A', '#171717']} rays={24} speed={1.4} />
      <Halftone />
      <Shake amount={3 + 24 * decayFrom(frame, HITS)} seed="cold-open">
        <Punch hits={HITS} amount={0.07}>
          <Tape y={200} angle={-8} speed={10} text="AI FILMHACK • 48 HOURS • " />
          <Tape y={1600} angle={7} speed={-10} text="FILM CHAOS • AI FILMHACK • " />
          <Slam at={0} rotate={-7} from={1.3} style={{ left: 70, top: 360 }}>
            <Interactive.Div
              name="WARNING tag"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 18,
                backgroundColor: '#FFD400',
                color: '#0A0A0A',
                fontFamily: 'MangoGrotesque',
                fontSize: 176,
                lineHeight: 1,
                padding: '18px 40px 6px 28px',
                border: '7px solid #0A0A0A',
                boxShadow: '14px 14px 0 #0A0A0A',
              }}
            >
              <WarningIcon size={136} />
              WARNING:
            </Interactive.Div>
          </Slam>
          <Slam at={12} rotate={4} style={{ left: 60, top: 610 }}>
            <Interactive.Div
              name="48 HOURS tag"
              style={{
                backgroundColor: '#C80528',
                color: '#FFFFFF',
                fontFamily: 'MangoGrotesque',
                fontSize: 250,
                lineHeight: 1,
                padding: '22px 44px 6px',
                border: '7px solid #0A0A0A',
                boxShadow: '14px 14px 0 #FFD400',
              }}
            >
              48 HOURS
            </Interactive.Div>
          </Slam>
          <Slam at={24} rotate={-4} style={{ left: 300, top: 930 }}>
            <Interactive.Div
              name="OF PURE tag"
              style={{
                backgroundColor: '#00D2E6',
                color: '#0A0A0A',
                fontFamily: 'MangoGrotesque',
                fontSize: 170,
                lineHeight: 1,
                padding: '18px 40px 6px',
                border: '7px solid #0A0A0A',
                boxShadow: '14px 14px 0 #0A0A0A',
              }}
            >
              OF PURE
            </Interactive.Div>
          </Slam>
          <Slam at={36} rotate={3} from={2.3} style={{ left: 0, right: 0, top: 1150, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="FILM CHAOS"
              style={{
                color: '#FFD400',
                fontFamily: 'MangoGrotesque',
                fontSize: 236,
                lineHeight: 1,
                WebkitTextStroke: '8px #0A0A0A',
                paintOrder: 'stroke fill',
                filter: 'drop-shadow(12px 12px 0 #FF1E50)',
              }}
            >
              FILM CHAOS!
            </Interactive.Div>
          </Slam>
          <Sticker at={38} x={890} y={520} size={210} color="#00E08A" angle={14}>
            48H!
          </Sticker>
          <Confetti at={36} x={540} y={1500} seed="cold-open" count={110} power={2400} />
        </Punch>
      </Shake>
    </AbsoluteFill>
  );
};
