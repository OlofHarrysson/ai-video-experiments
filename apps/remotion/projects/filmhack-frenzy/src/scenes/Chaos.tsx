import { useWindowedAudioData, visualizeAudio } from '@remotion/media-utils';
import React from 'react';
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { CYAN, DISPLAY, GREEN, HOT, INK, RED, SEG, WHITE, YELLOW } from '../brand';
import { Clapper } from '../components/Clapper';
import { Countdown, hms, remainingAt } from '../components/Countdown';
import { Sticker } from '../components/decor';
import { beatPulse, decayFrom, Shake } from '../components/motion';
import { beat, SCENES } from '../timing';

type Kind = 'mentors' | 'score' | 'clap' | 'snacks' | 'crew' | 'deadline' | 'clock' | 'hours' | 'film';

const BIG = (text: string, color: string, size: number, rotate: number, shadow: string) => (
  <div style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', rotate: `${rotate}deg` }}>
    <div style={{ fontFamily: DISPLAY, fontSize: size, lineHeight: 0.92, color, whiteSpace: 'pre-line', filter: `drop-shadow(10px 10px 0 ${shadow})` }}>{text}</div>
  </div>
);

const Equalizer: React.FC<{ readonly globalFrame: number }> = ({ globalFrame }) => {
  const { fps } = useVideoConfig();
  const { audioData, dataOffsetInSeconds } = useWindowedAudioData({ src: staticFile('soundtrack.wav'), frame: globalFrame, fps, windowInSeconds: 10 });
  if (!audioData) return null;
  const bins = visualizeAudio({ fps, frame: globalFrame, audioData, numberOfSamples: 32, optimizeFor: 'speed', dataOffsetInSeconds });
  const bars = bins.slice(0, 14).map((v) => Math.min(1, Math.max(0.04, (20 * Math.log10(v + 1e-6) + 70) / 50)));
  return (
    <div style={{ position: 'absolute', left: 40, right: 40, bottom: 260, height: 420, display: 'flex', alignItems: 'flex-end', gap: 10 }}>
      {bars.map((h, i) => (
        <div key={i} style={{ flex: 1, height: `${h * 100}%`, backgroundColor: INK, borderRadius: 8 }} />
      ))}
    </div>
  );
};

const Panel: React.FC<{ readonly kind: Kind; readonly frame: number; readonly globalFrame: number }> = ({ kind, frame, globalFrame }) => {
  switch (kind) {
    case 'mentors':
      return (
        <AbsoluteFill style={{ backgroundColor: YELLOW }}>
          {BIG('MENTORS!', INK, 150, -8, WHITE)}
          <Sticker at={0} x={400} y={210} size={200} color={HOT} ink={WHITE}>
            PROS
          </Sticker>
        </AbsoluteFill>
      );
    case 'score':
      return (
        <AbsoluteFill style={{ backgroundColor: CYAN }}>
          <Equalizer globalFrame={globalFrame} />
          <div style={{ position: 'absolute', left: 0, right: 0, top: 150, textAlign: 'center', fontFamily: DISPLAY, fontSize: 150, color: INK }}>SCORE!</div>
        </AbsoluteFill>
      );
    case 'clap':
      return (
        <AbsoluteFill style={{ backgroundColor: HOT, alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ rotate: '-6deg' }}>
            <Clapper width={440} arm={-32 * (1 - beatPulse(frame, 2.2))} />
          </div>
        </AbsoluteFill>
      );
    case 'snacks':
      return (
        <AbsoluteFill style={{ backgroundColor: INK }}>
          <div style={{ position: 'absolute', left: 0, right: 0, top: 290, textAlign: 'center', fontFamily: DISPLAY, fontSize: 150, lineHeight: 0.95, color: WHITE, rotate: '5deg' }}>
            SNACKS:
            <br />
            <span style={{ color: YELLOW }}>HANDLED.</span>
          </div>
        </AbsoluteFill>
      );
    case 'crew':
      return <AbsoluteFill style={{ backgroundColor: GREEN }}>{BIG('REAL\nCREW', INK, 190, 6, WHITE)}</AbsoluteFill>;
    case 'deadline':
      return <AbsoluteFill style={{ backgroundColor: WHITE }}>{BIG('REAL\nDEADLINE', RED, 150, -6, INK)}</AbsoluteFill>;
    case 'hours':
      return <AbsoluteFill style={{ backgroundColor: RED }}>{BIG('48H', YELLOW, 330, -4, INK)}</AbsoluteFill>;
    case 'clock':
      return (
        <AbsoluteFill style={{ backgroundColor: INK, alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ fontFamily: SEG, fontSize: 96, color: CYAN, rotate: '-90deg', whiteSpace: 'nowrap', textShadow: `0 0 20px ${CYAN}` }}>{hms(remainingAt(globalFrame))}</div>
        </AbsoluteFill>
      );
    case 'film':
      return (
        <AbsoluteFill style={{ backgroundColor: INK, overflow: 'hidden' }}>
          <div style={{ position: 'absolute', left: 150, width: 240, top: -400, height: 2400, translate: `0px ${(frame * 18) % 300}px`, backgroundColor: '#1b1b1b' }}>
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i} style={{ position: 'absolute', left: 30, top: 30 + i * 300, width: 180, height: 250, backgroundColor: [YELLOW, CYAN, HOT, GREEN][i % 4] }} />
            ))}
          </div>
        </AbsoluteFill>
      );
  }
};

const GRID_2: Kind[] = ['mentors', 'score', 'clap', 'snacks'];
const GRID_3: Kind[] = ['clock', 'mentors', 'crew', 'score', 'hours', 'deadline', 'clap', 'snacks', 'film'];

/** Beats 24–28: the frame splits into more and more panels, spins into the countdown, and switches off. */
export const Chaos: React.FC = () => {
  const frame = useCurrentFrame();
  const globalFrame = beat(SCENES.chaos[0]) + frame;
  const cols = frame < 24 ? 2 : 3;
  const kinds = cols === 2 ? GRID_2 : GRID_3;
  const w = 1080 / cols;
  const h = 1920 / cols;
  const spin = interpolate(frame, [36, 44], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic) });
  const squashY = interpolate(frame, [44, 46], [1, 0.006], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad) });
  const squashX = interpolate(frame, [46, 47], [1, 0.02], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const glow = interpolate(frame, [43, 46], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ scale: `${squashX} ${squashY}` }}>
        <Shake amount={6 + 26 * decayFrom(frame, [0, 12, 24, 30, 36, 42])} seed="chaos">
          <AbsoluteFill style={{ scale: String(1 + 1.2 * spin), rotate: `${28 * spin}deg` }}>
            {kinds.map((kind, i) => (
              <div
                key={`${cols}-${kind}-${i}`}
                style={{
                  position: 'absolute',
                  left: (i % cols) * w,
                  top: Math.floor(i / cols) * h,
                  width: w,
                  height: h,
                  overflow: 'hidden',
                  outline: `6px solid ${INK}`,
                }}
              >
                <div style={{ width: 540, height: 960, scale: String(w / 540), transformOrigin: '0 0', position: 'relative' }}>
                  <Panel kind={kind} frame={frame} globalFrame={globalFrame} />
                </div>
              </div>
            ))}
          </AbsoluteFill>
          <div style={{ opacity: interpolate(frame, [36, 38], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
            <Countdown globalFrame={globalFrame} x={90} y={810} width={900} />
          </div>
        </Shake>
        <AbsoluteFill style={{ backgroundColor: WHITE, opacity: glow }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
