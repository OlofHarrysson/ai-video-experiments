import { noise2D } from '@remotion/noise';
import React from 'react';
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from 'remotion';
import { FRAMES_PER_BEAT } from '../timing';

/** 1 on each hit frame, decaying exponentially after it. */
export const decayFrom = (frame: number, hits: readonly number[], tau = 3) => {
  let value = 0;
  for (const hit of hits) if (frame >= hit) value = Math.max(value, Math.exp(-(frame - hit) / tau));
  return value;
};

/** A pulse on every beat of the local timeline. */
export const beatPulse = (frame: number, tau = 3) => Math.exp(-(((frame % FRAMES_PER_BEAT) + FRAMES_PER_BEAT) % FRAMES_PER_BEAT) / tau);

type SlamProps = {
  readonly at: number;
  readonly rotate?: number;
  readonly from?: number;
  readonly split?: number;
  readonly style?: React.CSSProperties;
  readonly children: React.ReactNode;
};

/** Slams content in at frame `at`: overshoot, squash, a settling twist and a burst of RGB split. */
export const Slam: React.FC<SlamProps> = ({ at, rotate = 0, from = 1.9, split = 5, style, children }) => {
  const frame = useCurrentFrame();
  const f = frame - at;
  if (f < 0) return null;
  const rgb = split + 24 * Math.exp(-f / 2.2);
  return (
    <div
      style={{
        position: 'absolute',
        ...style,
        scale: String(interpolate(f, [0, 2, 6], [from, 0.94, 1], { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) })),
        rotate: `${rotate + interpolate(f, [0, 6], [-10, 0], { extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) })}deg`,
        textShadow: `${-rgb}px 0 0 rgba(0,228,255,0.9), ${rgb}px 0 0 rgba(255,30,80,0.9)`,
      }}
    >
      {children}
    </div>
  );
};

type PunchProps = {
  readonly hits?: readonly number[];
  readonly amount?: number;
  readonly everyBeat?: boolean;
  readonly children: React.ReactNode;
};

/** Zoom punch on the given frames (and optionally every beat). */
export const Punch: React.FC<PunchProps> = ({ hits = [], amount = 0.06, everyBeat = false, children }) => {
  const frame = useCurrentFrame();
  const k = Math.max(decayFrom(frame, hits), everyBeat ? 0.6 * beatPulse(frame) : 0);
  return <AbsoluteFill style={{ scale: String(1 + amount * k) }}>{children}</AbsoluteFill>;
};

type ShakeProps = {
  readonly amount: number;
  readonly seed?: string;
  readonly children: React.ReactNode;
};

/** Smooth camera shake from simplex noise; `amount` is the peak offset in px. */
export const Shake: React.FC<ShakeProps> = ({ amount, seed = 'shake', children }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        translate: `${noise2D(`${seed}-x`, frame * 0.45, 0) * amount}px ${noise2D(`${seed}-y`, frame * 0.45, 0) * amount}px`,
        rotate: `${noise2D(`${seed}-r`, frame * 0.3, 0) * amount * 0.06}deg`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
