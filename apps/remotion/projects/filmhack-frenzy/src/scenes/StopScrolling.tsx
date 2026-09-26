import React from 'react';
import { AbsoluteFill, Easing, interpolate, Interactive, Sequence, useCurrentFrame } from 'remotion';
import { Halftone, Tape } from '../components/decor';
import { decayFrom, Shake, Slam } from '../components/motion';

const HITS = [0, 6, 12, 18, 24, 30, 36];

/** Beats 4–8: STOP stutters three times, then the yellow flip to START CREATING and the build. */
export const StopScrolling: React.FC = () => {
  const frame = useCurrentFrame();
  const build = interpolate(frame, [36, 45], [1, 1.32], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) });
  return (
    <AbsoluteFill style={{ backgroundColor: '#0A0A0A', overflow: 'hidden' }}>
      <Sequence name="Stop scrolling" durationInFrames={24} layout="none">
        <Halftone />
        <Shake amount={4 + 22 * decayFrom(frame, HITS)} seed="stop">
          <Slam at={6} rotate={-6} style={{ left: 0, right: 0, top: 250, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="STOP outline"
              style={{ color: 'transparent', fontFamily: 'MangoGrotesque', fontSize: 330, lineHeight: 1, WebkitTextStroke: '7px #FFFFFF' }}
            >
              STOP
            </Interactive.Div>
          </Slam>
          <Slam at={0} style={{ left: 0, right: 0, top: 520, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="STOP"
              style={{ color: '#FF1E50', fontFamily: 'MangoGrotesque', fontSize: 370, lineHeight: 1, filter: 'drop-shadow(12px 12px 0 #FFFFFF)' }}
            >
              STOP
            </Interactive.Div>
          </Slam>
          <Slam at={12} rotate={5} style={{ left: 0, right: 0, top: 820, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="STOP cyan outline"
              style={{ color: 'transparent', fontFamily: 'MangoGrotesque', fontSize: 330, lineHeight: 1, WebkitTextStroke: '7px #00D2E6' }}
            >
              STOP
            </Interactive.Div>
          </Slam>
          <Slam at={18} rotate={-3} style={{ left: 0, right: 0, top: 1140, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="SCROLLING tag"
              style={{
                backgroundColor: '#FFD400',
                color: '#0A0A0A',
                fontFamily: 'MangoGrotesque',
                fontSize: 190,
                lineHeight: 1,
                padding: '18px 44px 6px',
                border: '7px solid #0A0A0A',
                boxShadow: '14px 14px 0 #FF1E50',
              }}
            >
              SCROLLING.
            </Interactive.Div>
          </Slam>
        </Shake>
      </Sequence>
      <Sequence name="Start creating" from={24} durationInFrames={21} layout="none">
        <AbsoluteFill style={{ backgroundColor: '#FFD400', scale: String(build) }}>
          <Shake amount={6 + 30 * decayFrom(frame, [24, 30, 36, 39, 42])} seed="start">
            <Slam at={0} rotate={-4} style={{ left: 0, right: 0, top: 380, display: 'flex', justifyContent: 'center' }}>
              <Interactive.Div
                name="START"
                style={{ color: '#0A0A0A', fontFamily: 'MangoGrotesque', fontSize: 400, lineHeight: 1, filter: 'drop-shadow(14px 14px 0 #00D2E6)' }}
              >
                START
              </Interactive.Div>
            </Slam>
            <Slam at={6} rotate={3} style={{ left: 0, right: 0, top: 780, display: 'flex', justifyContent: 'center' }}>
              <Interactive.Div
                name="CREATING"
                style={{ color: '#C80528', fontFamily: 'MangoGrotesque', fontSize: 270, lineHeight: 1, filter: 'drop-shadow(12px 12px 0 #0A0A0A)' }}
              >
                CREATING.
              </Interactive.Div>
            </Slam>
            <Sequence from={12} layout="none">
              <Tape y={1120} angle={-11} speed={-26} text="AI FILMHACK • STOP WAITING • START CREATING • " color="#0A0A0A" ink="#FFD400" offset={-600} />
              <Tape y={1260} angle={9} speed={26} text="48 HOURS • ONE FILM • BIG SCREEN • " color="#0A0A0A" ink="#FFFFFF" />
            </Sequence>
          </Shake>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
