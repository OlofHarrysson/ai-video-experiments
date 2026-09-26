import { fitText } from '@remotion/layout-utils';
import React from 'react';
import { AbsoluteFill, Easing, interpolate, Interactive, Sequence, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { DISPLAY, HOT, INK, MONO, WHITE } from '../brand';
import { Rays, Sticker } from '../components/decor';
import { PinIcon } from '../components/icons';
import { decayFrom, Shake, Slam } from '../components/motion';

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const Caption: React.FC<{ readonly top: number; readonly color: string; readonly children: React.ReactNode }> = ({ top, color, children }) => (
  <div style={{ position: 'absolute', left: 0, right: 0, top, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 46, letterSpacing: 6, color, textShadow: 'none' }}>
    {children}
  </div>
);

const Logo: React.FC = () => {
  const frame = useCurrentFrame();
  const size = Math.min(330, fitText({ text: 'AI FILMHACK', withinWidth: 960, fontFamily: DISPLAY }).fontSize);
  return (
    <AbsoluteFill style={{ backgroundColor: '#C80528', overflow: 'hidden' }}>
      <Rays colors={['#C80528', '#A6031F']} rays={26} speed={1.6} />
      <Shake amount={4 + 28 * decayFrom(frame, [0, 6, 12])} seed="logo">
        <Slam at={0} from={2.6} split={7} style={{ left: 0, right: 0, top: 560, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: size, lineHeight: 1, color: WHITE, filter: `drop-shadow(14px 14px 0 ${INK})` }}>AI FILMHACK</div>
        </Slam>
        <Slam at={6} rotate={-3} style={{ left: 0, right: 0, top: 910, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="Europe's first tag"
            style={{ backgroundColor: '#0A0A0A', color: '#FFFFFF', fontFamily: 'MangoGrotesque', fontSize: 100, lineHeight: 1, padding: '14px 30px 2px' }}
          >
            EUROPE'S FIRST HYBRID
          </Interactive.Div>
        </Slam>
        <Slam at={12} rotate={2} style={{ left: 0, right: 0, top: 1070, display: 'flex', justifyContent: 'center' }}>
          <Interactive.Div
            name="AI x FILM tag"
            style={{
              backgroundColor: '#FFD400',
              color: '#0A0A0A',
              fontFamily: 'MangoGrotesque',
              fontSize: 100,
              lineHeight: 1,
              padding: '14px 30px 2px',
              border: '6px solid #0A0A0A',
            }}
          >
            AI × FILM CHALLENGE
          </Interactive.Div>
        </Slam>
        <Sticker at={18} x={880} y={400} size={220} color="#FFD400" angle={16}>
          1ST!
        </Sticker>
      </Shake>
    </AbsoluteFill>
  );
};

const DateCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const flip = spring({ frame, fps, config: { damping: 11, stiffness: 240, mass: 0.5 } });
  return (
    <AbsoluteFill style={{ backgroundColor: '#FFD400', overflow: 'hidden' }}>
      <Rays colors={['#FFD400', '#F2C200']} rays={22} speed={2} />
      <Shake amount={4 + 22 * decayFrom(frame, [0])} seed="date">
        <Caption top={300} color={INK}>
          WHEN
        </Caption>
        <div
          style={{
            position: 'absolute',
            left: 170,
            top: 390,
            width: 740,
            height: 720,
            rotate: '-5deg',
            scale: `1 ${flip}`,
            backgroundColor: WHITE,
            border: `9px solid ${INK}`,
            borderRadius: 30,
            boxShadow: `18px 18px 0 ${INK}`,
            overflow: 'hidden',
          }}
        >
          <div style={{ height: 170, backgroundColor: HOT, borderBottom: `9px solid ${INK}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: DISPLAY, fontSize: 130, color: WHITE }}>
            NOVEMBER
          </div>
          <div style={{ textAlign: 'center', fontFamily: DISPLAY, fontSize: 330, lineHeight: 1.1, color: INK }}>12–15</div>
          <div style={{ textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 52, letterSpacing: 10, color: INK }}>2026</div>
        </div>
        <Caption top={1200} color={INK}>
          THU → SUN
        </Caption>
      </Shake>
    </AbsoluteFill>
  );
};

const Venue: React.FC = () => {
  const frame = useCurrentFrame();
  const bounce = Math.abs(Math.sin(frame / 2.4)) * 90 * Math.exp(-frame / 10);
  const uni = Math.min(210, fitText({ text: 'FILMUNIVERSITÄT', withinWidth: 940, fontFamily: DISPLAY }).fontSize);
  const place = Math.min(270, fitText({ text: 'BABELSBERG', withinWidth: 940, fontFamily: DISPLAY }).fontSize);
  return (
    <AbsoluteFill style={{ backgroundColor: '#00D2E6', overflow: 'hidden' }}>
      <Rays colors={['#00D2E6', '#00C0D4']} rays={22} speed={-2} origin={[0.5, 0.2]} />
      <Shake amount={4 + 22 * decayFrom(frame, [0])} seed="venue">
        <div style={{ position: 'absolute', left: 540 - 115, top: 250, translate: `0px ${-bounce}px` }}>
          <PinIcon size={230} color={INK} fill={HOT} />
        </div>
        <Slam at={0} rotate={-3} style={{ left: 0, right: 0, top: 560, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: uni, lineHeight: 1, color: INK }}>FILMUNIVERSITÄT</div>
        </Slam>
        <Slam at={3} rotate={2} style={{ left: 0, right: 0, top: 560 + uni * 0.95, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: place, lineHeight: 1, color: WHITE, filter: `drop-shadow(12px 12px 0 ${INK})` }}>BABELSBERG</div>
        </Slam>
        <Caption top={1150} color={INK}>
          POTSDAM · NEXT TO BERLIN
        </Caption>
      </Shake>
    </AbsoluteFill>
  );
};

const Free: React.FC = () => {
  const frame = useCurrentFrame();
  const swing = 16 * Math.sin(frame / 2.6) * Math.exp(-frame / 14);
  const size = Math.min(470, fitText({ text: 'FREE.', withinWidth: 900, fontFamily: DISPLAY }).fontSize);
  return (
    <AbsoluteFill style={{ backgroundColor: '#00E08A', overflow: 'hidden' }}>
      <Rays colors={['#00E08A', '#00CC7D']} rays={22} speed={2.4} origin={[0.5, 0.35]} />
      <Shake amount={4 + 22 * decayFrom(frame, [0, 6])} seed="free">
        <Slam at={0} from={2.2} rotate={-4} style={{ left: 0, right: 0, top: 360, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: size, lineHeight: 1, color: INK, filter: `drop-shadow(16px 16px 0 ${WHITE})` }}>FREE.</div>
        </Slam>
        <div
          style={{
            position: 'absolute',
            left: 540 - 200,
            top: 900,
            width: 400,
            height: 230,
            transformOrigin: '8% 50%',
            rotate: `${-8 + swing}deg`,
            scale: String(interpolate(frame, [6, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2.2)) })),
            backgroundColor: WHITE,
            border: `9px solid ${INK}`,
            borderRadius: '24px 24px 24px 24px',
            boxShadow: `14px 14px 0 ${INK}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: DISPLAY,
            fontSize: 190,
            color: HOT,
          }}
        >
          <div style={{ position: 'absolute', left: 26, top: 90, width: 34, height: 34, borderRadius: '50%', border: `8px solid ${INK}`, backgroundColor: '#00E08A' }} />
          €0
        </div>
        <Caption top={1230} color={INK}>
          APPLICATION-BASED
        </Caption>
      </Shake>
    </AbsoluteFill>
  );
};

const Spots: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: '#C80528', overflow: 'hidden' }}>
      <Rays colors={['#C80528', '#B0041F']} rays={30} speed={-2.4} />
      <Shake amount={8 + 26 * decayFrom(frame, [0, 6, 12, 18])} seed="spots">
        <Slam at={0} rotate={-5} style={{ left: 0, right: 0, top: 300, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: 220, lineHeight: 1, color: WHITE }}>ONLY</div>
        </Slam>
        <Slam at={3} from={2.6} split={8} style={{ left: 0, right: 0, top: 500, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: 540, lineHeight: 1, color: '#FFD400', WebkitTextStroke: `10px ${INK}`, paintOrder: 'stroke fill', filter: `drop-shadow(18px 18px 0 ${INK})` }}>
            100
          </div>
        </Slam>
        <Slam at={6} rotate={4} style={{ left: 0, right: 0, top: 1050, display: 'flex', justifyContent: 'center' }}>
          <div style={{ fontFamily: DISPLAY, fontSize: 250, lineHeight: 1, color: WHITE, filter: `drop-shadow(12px 12px 0 ${INK})` }}>SPOTS!</div>
        </Slam>
      </Shake>
    </AbsoluteFill>
  );
};

/** Beats 40–52: logo slam, then date, venue, price and capacity, two beats each. */
export const Facts: React.FC = () => (
  <AbsoluteFill>
    <Sequence name="Logo" durationInFrames={48} premountFor={30}>
      <Logo />
    </Sequence>
    <Sequence name="Date" from={48} durationInFrames={24} premountFor={30}>
      <DateCard />
    </Sequence>
    <Sequence name="Venue" from={72} durationInFrames={24} premountFor={30}>
      <Venue />
    </Sequence>
    <Sequence name="Free" from={96} durationInFrames={24} premountFor={30}>
      <Free />
    </Sequence>
    <Sequence name="Spots" from={120} durationInFrames={24} premountFor={30}>
      <Spots />
    </Sequence>
  </AbsoluteFill>
);
