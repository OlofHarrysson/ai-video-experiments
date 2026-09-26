import React from 'react';
import { AbsoluteFill, Easing, interpolate, Interactive, random, Sequence, useCurrentFrame } from 'remotion';
import { Clapper } from '../components/Clapper';
import { Confetti, Rays, Sticker } from '../components/decor';
import { decayFrom, Shake, Slam } from '../components/motion';

const HITS = [0, 12, 24, 36];

const Spotlight: React.FC<{ readonly x: number; readonly angle: number; readonly color: string }> = ({ x, angle, color }) => (
  <div
    style={{
      position: 'absolute',
      left: x - 260,
      top: 0,
      width: 520,
      height: 2100,
      transformOrigin: '50% 100%',
      rotate: `${angle}deg`,
      background: `linear-gradient(to top, ${color} 0%, rgba(255,255,255,0) 85%)`,
      clipPath: 'polygon(46% 100%, 54% 100%, 100% 0%, 0% 0%)',
      mixBlendMode: 'screen',
      opacity: 0.55,
    }}
  />
);

const Sparkles: React.FC<{ readonly seed: string }> = ({ seed }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {Array.from({ length: 26 }, (_, i) => {
        const r = (k: string) => random(`${seed}-${i}-${k}`);
        const twinkle = Math.max(0, Math.sin(frame * (0.5 + r('s')) + r('p') * 6));
        const size = 14 + r('z') * 26;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: r('x') * 1080,
              top: 200 + r('y') * 1300,
              width: size,
              height: size,
              backgroundColor: '#FFD400',
              clipPath: 'polygon(50% 0%, 60% 40%, 100% 50%, 60% 60%, 50% 100%, 40% 60%, 0% 50%, 40% 40%)',
              scale: String(twinkle),
            }}
          />
        );
      })}
    </>
  );
};

/** Beats 8–12, drop one: LIGHTS! CAMERA! ACTION! with the slate clapping on beat 10. */
export const LightsCameraAction: React.FC = () => {
  const frame = useCurrentFrame();
  const sweep = Math.sin(frame / 5) * 14;
  const drop = interpolate(frame, [18, 23], [-1300, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad) });
  const arm = interpolate(frame, [18, 21, 24], [-34, -34, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad) });
  return (
    <AbsoluteFill style={{ backgroundColor: '#07070F', overflow: 'hidden' }}>
      <Sequence name="Action rays" from={24} layout="none">
        <Rays colors={['#00B7C9', '#00D2E6']} rays={20} speed={2.2} origin={[0.5, 0.38]} />
      </Sequence>
      <Shake amount={4 + 26 * decayFrom(frame, HITS)} seed="lca">
        <Sequence name="Lights" durationInFrames={24} layout="none">
          <Spotlight x={150} angle={20 + sweep} color="#FFD400" />
          <Spotlight x={930} angle={-20 - sweep} color="#FFFFFF" />
          <Sparkles seed="lights" />
          <Slam at={0} rotate={-5} style={{ left: 0, right: 0, top: 560, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="LIGHTS"
              style={{ color: '#FFD400', fontFamily: 'MangoGrotesque', fontSize: 330, lineHeight: 1, filter: 'drop-shadow(0 0 40px rgba(255,212,0,0.8))' }}
            >
              LIGHTS!
            </Interactive.Div>
          </Slam>
        </Sequence>
        <Sequence name="Camera" from={12} durationInFrames={12} layout="none">
          <div style={{ position: 'absolute', left: 70, right: 70, top: 240, bottom: 380, border: '10px solid rgba(255,255,255,0.85)' }} />
          <div style={{ position: 'absolute', left: 110, top: 280, fontFamily: 'Geist Mono', fontWeight: 700, fontSize: 44, color: '#FF1E50', letterSpacing: 4 }}>● REC</div>
          <div style={{ position: 'absolute', right: 110, top: 280, fontFamily: 'Geist Mono', fontWeight: 700, fontSize: 44, color: '#FFFFFF', letterSpacing: 4 }}>4K • 24 FPS</div>
          <Slam at={0} rotate={4} style={{ left: 0, right: 0, top: 1000, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="CAMERA tag"
              style={{
                backgroundColor: '#C80528',
                color: '#FFFFFF',
                fontFamily: 'MangoGrotesque',
                fontSize: 250,
                lineHeight: 1,
                padding: '22px 44px 6px',
                border: '7px solid #0A0A0A',
                boxShadow: '14px 14px 0 #FFFFFF',
              }}
            >
              CAMERA!
            </Interactive.Div>
          </Slam>
        </Sequence>
        <div style={{ position: 'absolute', left: 170, top: 300, translate: `0px ${drop}px`, rotate: '-5deg' }}>
          <Clapper width={740} arm={arm} />
        </div>
        <Slam at={24} rotate={-3} from={2.4} style={{ left: 0, right: 0, top: 1000, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="ACTION"
            style={{
              color: '#FFFFFF',
              fontFamily: 'MangoGrotesque',
              fontSize: 330,
              lineHeight: 1,
              WebkitTextStroke: '9px #0A0A0A',
              paintOrder: 'stroke fill',
              filter: 'drop-shadow(14px 14px 0 #0A0A0A)',
            }}
          >
            ACTION!
          </Interactive.Div>
        </Slam>
        <Sticker at={36} x={870} y={1360} size={230} color="#FFD400" angle={12}>
          48H!
        </Sticker>
        <Sticker at={38} x={200} y={1380} size={210} color="#00E08A" angle={-10} spin={-1.4}>
          FREE!
        </Sticker>
        <Confetti at={24} x={540} y={700} seed="action" count={120} power={2600} spread={220} />
      </Shake>
    </AbsoluteFill>
  );
};
