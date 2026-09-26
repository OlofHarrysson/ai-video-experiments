import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { CYAN, GREEN, INK, MONO, DISPLAY, WHITE, YELLOW } from '../brand';
import { Countdown } from '../components/Countdown';
import { Rays } from '../components/decor';
import { CheckIcon } from '../components/icons';
import { decayFrom, Shake } from '../components/motion';
import { beat, SCENES } from '../timing';

const PROMPTS = ['a pigeon directing a noir film', 'grandma with a bazooka, slow-mo', "the moon, but it's a disco ball", '48 hours. one film. go!'];

const clamp01 = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const PromptCard: React.FC<{ readonly index: number; readonly text: string }> = ({ index, text }) => {
  const frame = useCurrentFrame();
  const t0 = beat(index);
  if (frame < t0) return null;
  const typed = Math.ceil(text.length * interpolate(frame, [t0 + 1, t0 + 8], [0, 1], clamp01));
  const progress = interpolate(frame, [t0 + 5, t0 + 9], [0, 1], clamp01);
  const done = frame >= t0 + 9;
  const stamp = interpolate(frame, [t0 + 9, t0 + 12], [2.2, 1], { ...clamp01, easing: Easing.out(Easing.back(2)) });
  return (
    <div
      style={{
        position: 'absolute',
        left: 40 + (index % 2) * 30,
        top: 560 + index * 222,
        width: 970,
        height: 206,
        rotate: `${[-2.5, 2, -1.5, 2.5][index]}deg`,
        translate: `${interpolate(frame, [t0, t0 + 4], [1100, 0], { ...clamp01, easing: Easing.out(Easing.cubic) })}px 0px`,
        backgroundColor: '#131316',
        border: `5px solid ${CYAN}`,
        borderRadius: 22,
        boxShadow: `14px 14px 0 ${INK}`,
        padding: '18px 28px',
        boxSizing: 'border-box',
        textShadow: 'none',
      }}
    >
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 26, letterSpacing: 4, color: CYAN }}>PROMPT {String(index + 1).padStart(2, '0')}</div>
      <div style={{ fontFamily: MONO, fontWeight: 500, fontSize: 46, color: WHITE, marginTop: 10, whiteSpace: 'nowrap' }}>
        {'> '}
        {text.slice(0, typed)}
        {typed < text.length && frame % 4 < 2 ? <span style={{ display: 'inline-block', width: 20, height: 38, marginLeft: 4, verticalAlign: -6, backgroundColor: CYAN }} /> : null}
      </div>
      <div style={{ position: 'absolute', left: 28, right: 28, bottom: 22, height: 14, backgroundColor: '#26262b', borderRadius: 7 }}>
        <div style={{ width: `${progress * 100}%`, height: '100%', backgroundColor: done ? GREEN : YELLOW, borderRadius: 7 }} />
      </div>
      {done ? (
        <div
          style={{
            position: 'absolute',
            right: -30,
            top: -44,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            backgroundColor: GREEN,
            color: INK,
            fontFamily: DISPLAY,
            fontSize: 70,
            lineHeight: 1,
            padding: '10px 22px 2px 14px',
            border: `6px solid ${INK}`,
            rotate: '-9deg',
            scale: String(stamp),
          }}
        >
          <CheckIcon size={58} />
          RENDERED
        </div>
      ) : null}
    </div>
  );
};

/** Beats 12–16: the clock starts and absurd prompts get typed, generated and stamped on every beat. */
export const Prompts: React.FC = () => {
  const frame = useCurrentFrame();
  const globalFrame = beat(SCENES.prompts[0]) + frame;
  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: 'hidden' }}>
      <Rays colors={['#0A0A0A', '#10141a']} rays={20} speed={-1.6} origin={[0.5, 0.2]} />
      <AbsoluteFill
        style={{
          backgroundImage: 'linear-gradient(rgba(0,210,230,0.07) 2px, transparent 2px), linear-gradient(90deg, rgba(0,210,230,0.07) 2px, transparent 2px)',
          backgroundSize: '90px 90px',
          backgroundPosition: `0px ${-frame * 6}px`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: -60,
          top: 1480,
          rotate: '-8deg',
          fontFamily: DISPLAY,
          fontSize: 300,
          lineHeight: 1,
          color: 'transparent',
          WebkitTextStroke: '4px rgba(0,210,230,0.35)',
          whiteSpace: 'nowrap',
          translate: `${-frame * 9}px 0px`,
        }}
      >
        GENERATE • GENERATE • GENERATE
      </div>
      <Shake amount={3 + 18 * decayFrom(frame, [0, 12, 24, 36])} seed="prompts">
        <Countdown globalFrame={globalFrame} x={140} y={230} width={800} />
        {PROMPTS.map((text, i) => (
          <PromptCard key={text} index={i} text={text} />
        ))}
      </Shake>
    </AbsoluteFill>
  );
};
