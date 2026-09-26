import React from 'react';
import { AbsoluteFill, Easing, interpolate, Interactive, random, useCurrentFrame } from 'remotion';
import { DISPLAY, MONO } from '../brand';
import { Shake, Slam } from '../components/motion';

const PAPER = '#F3EAD7';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const Leader: React.FC<{ readonly frame: number }> = ({ frame }) => {
  const local = frame - 24;
  if (local < 0) return null;
  const n = Math.min(2, Math.floor(local / 6));
  const sweep = local >= 18 ? 360 : ((local % 6) / 6) * 360;
  const zoom = interpolate(frame, [42, 47], [1, 2.6], { ...clamp, easing: Easing.in(Easing.cubic) });
  const flicker = 0.86 + 0.14 * random(`flicker-${frame}`);
  return (
    <div style={{ position: 'absolute', left: 540 - 340, top: 1080 - 340, width: 680, height: 680, scale: String(zoom), opacity: flicker }}>
      <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', backgroundColor: '#1b1712', background: `conic-gradient(rgba(243,234,215,0.26) ${sweep}deg, #1b1712 ${sweep}deg)` }} />
      <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: `7px solid ${PAPER}` }} />
      <div style={{ position: 'absolute', inset: 60, borderRadius: '50%', border: `5px solid ${PAPER}` }} />
      <div style={{ position: 'absolute', left: -120, right: -120, top: 337, height: 6, backgroundColor: PAPER }} />
      <div style={{ position: 'absolute', top: -120, bottom: -120, left: 337, width: 6, backgroundColor: PAPER }} />
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: DISPLAY, fontSize: 420, lineHeight: 1, color: PAPER, textShadow: '10px 10px 0 #000' }}>
        {3 - n}
      </div>
    </div>
  );
};

/** Beats 28–32: the clock switches off, "…and then" types out, SUNDAY. lands, and a film leader counts down into the drop. */
export const Sunday: React.FC = () => {
  const frame = useCurrentFrame();
  const typed = Math.ceil(10 * interpolate(frame, [6, 13], [0, 1], clamp));
  const lift = interpolate(frame, [22, 27], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const shake = interpolate(frame, [18, 47], [2, 26], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: '#050403', overflow: 'hidden' }}>
      <div
        style={{
          position: 'absolute',
          left: 540 - interpolate(frame, [0, 3], [520, 4], clamp),
          width: 2 * interpolate(frame, [0, 3], [520, 4], clamp),
          top: 956,
          height: 8,
          backgroundColor: '#FFFFFF',
          boxShadow: '0 0 40px 10px rgba(255,255,255,0.8)',
          opacity: interpolate(frame, [0, 7], [1, 0], clamp),
        }}
      />
      <Shake amount={shake} seed="sunday">
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: interpolate(lift, [0, 1], [700, 210]),
            textAlign: 'center',
            fontFamily: MONO,
            fontWeight: 500,
            fontSize: 64,
            color: 'rgba(243,234,215,0.85)',
            opacity: 1 - 0.4 * lift,
          }}
        >
          {'…and then'.slice(0, typed)}
          {frame >= 6 && frame < 20 && frame % 6 < 3 ? <span style={{ display: 'inline-block', width: 30, height: 58, marginLeft: 6, verticalAlign: -8, backgroundColor: PAPER }} /> : null}
        </div>
        <div style={{ position: 'absolute', left: 0, right: 0, top: interpolate(lift, [0, 1], [820, 300]), scale: String(1 - 0.42 * lift) }}>
          <Slam at={18} from={2.2} style={{ left: 0, right: 0, top: 0, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div name="SUNDAY" style={{ fontFamily: 'MangoGrotesque', fontSize: 330, lineHeight: 1, color: '#F3EAD7' }}>
              SUNDAY.
            </Interactive.Div>
          </Slam>
        </div>
        <Leader frame={frame} />
        {frame >= 24
          ? Array.from({ length: 3 }, (_, i) => (
              <div
                key={i}
                style={{ position: 'absolute', top: 0, bottom: 0, left: random(`scratch-${frame}-${i}`) * 1080, width: 2, backgroundColor: 'rgba(243,234,215,0.25)' }}
              />
            ))
          : null}
      </Shake>
    </AbsoluteFill>
  );
};
