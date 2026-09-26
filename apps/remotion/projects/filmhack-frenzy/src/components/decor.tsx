import { starburst } from '@remotion/effects/starburst';
import React from 'react';
import { AbsoluteFill, random, Solid, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { CYAN, DISPLAY, HOT, INK, PALETTE, WHITE, YELLOW } from '../brand';

type TapeProps = {
  readonly y: number;
  readonly angle: number;
  /** Pixels per frame; negative scrolls the other way. */
  readonly speed: number;
  readonly text: string;
  readonly height?: number;
  readonly color?: string;
  readonly ink?: string;
  readonly offset?: number;
};

/** Caution tape with a scrolling slogan and striped edges. */
export const Tape: React.FC<TapeProps> = ({ y, angle, speed, text, height = 124, color = YELLOW, ink = INK, offset = 0 }) => {
  const frame = useCurrentFrame();
  const stripes = `repeating-linear-gradient(-45deg, ${ink} 0 16px, ${color} 16px 32px)`;
  return (
    <div
      style={{
        position: 'absolute',
        left: -420,
        top: y - height / 2,
        width: 1920,
        height,
        rotate: `${angle}deg`,
        backgroundColor: color,
        overflow: 'hidden',
        boxShadow: '0 12px 0 rgba(0,0,0,0.35)',
      }}
    >
      <div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 14, backgroundImage: stripes }} />
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 14, backgroundImage: stripes }} />
      <div
        style={{
          position: 'absolute',
          top: 14,
          bottom: 14,
          left: 0,
          display: 'flex',
          alignItems: 'center',
          whiteSpace: 'nowrap',
          translate: `${offset - 1200 - frame * speed}px 0px`,
          fontFamily: DISPLAY,
          fontSize: (height - 28) * 0.82,
          color: ink,
          textShadow: 'none',
        }}
      >
        {Array.from({ length: 14 }, () => text).join('')}
      </div>
    </div>
  );
};

const burstPath = (points: number, outer: number, inner: number) => {
  const coords: string[] = [];
  for (let i = 0; i < points * 2; i++) {
    const r = i % 2 === 0 ? outer : inner;
    const a = (i * Math.PI) / points - Math.PI / 2;
    coords.push(`${(outer + r * Math.cos(a)).toFixed(1)},${(outer + r * Math.sin(a)).toFixed(1)}`);
  }
  return coords.join(' ');
};

type StickerProps = {
  readonly at: number;
  readonly x: number;
  readonly y: number;
  readonly size: number;
  readonly color: string;
  readonly ink?: string;
  readonly spin?: number;
  readonly angle?: number;
  readonly points?: number;
  readonly children: React.ReactNode;
};

/** Pop-art starburst badge that springs in and spins. */
export const Sticker: React.FC<StickerProps> = ({ at, x, y, size, color, ink = INK, spin = 1.2, angle = -12, points = 16, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - at;
  if (f < 0) return null;
  const pop = spring({ frame: f, fps, config: { damping: 8, stiffness: 190, mass: 0.5 } });
  const half = size / 2;
  return (
    <div
      style={{
        position: 'absolute',
        left: x - half,
        top: y - half,
        width: size,
        height: size,
        scale: String(pop),
        rotate: `${angle + Math.sin(f / 6) * 6}deg`,
        textShadow: 'none',
      }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ position: 'absolute', rotate: `${spin * f}deg`, overflow: 'visible' }}>
        <polygon points={burstPath(points, half, half * 0.8)} fill={INK} transform="translate(8 10)" />
        <polygon points={burstPath(points, half, half * 0.8)} fill={color} stroke={ink} strokeWidth={7} strokeLinejoin="round" />
      </svg>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          fontFamily: DISPLAY,
          color: ink,
          fontSize: size * 0.26,
          lineHeight: 0.9,
        }}
      >
        {children}
      </div>
    </div>
  );
};

type ConfettiProps = {
  readonly at: number;
  readonly x: number;
  readonly y: number;
  readonly seed: string;
  readonly count?: number;
  /** Launch direction in degrees, 0 is straight up. */
  readonly direction?: number;
  readonly spread?: number;
  readonly power?: number;
};

/** Deterministic confetti burst with drag, gravity, spin and flutter. */
export const Confetti: React.FC<ConfettiProps> = ({ at, x, y, seed, count = 90, direction = 0, spread = 120, power = 2200 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame - at) / fps;
  if (t < 0 || t > 3.5) return null;
  const drag = 1.7;
  return (
    <>
      {Array.from({ length: count }, (_, i) => {
        const r = (k: string) => random(`${seed}-${i}-${k}`);
        const angle = ((direction + (r('a') - 0.5) * spread) * Math.PI) / 180;
        const speed = power * (0.35 + 0.65 * r('v'));
        const travel = (1 - Math.exp(-drag * t)) / drag;
        const px = x + Math.sin(angle) * speed * travel;
        const py = y - Math.cos(angle) * speed * travel + 0.5 * 1500 * t * t;
        const w = 16 + r('w') * 18;
        const h = 9 + r('h') * 12;
        const flutter = Math.abs(Math.cos(t * (5 + r('f') * 9) + r('p') * 6));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: px,
              top: py,
              width: w,
              height: Math.max(2, h * flutter),
              backgroundColor: PALETTE[Math.floor(r('c') * PALETTE.length)],
              borderRadius: r('round') > 0.72 ? '50%' : 2,
              rotate: `${(r('s') - 0.5) * 1600 * t}deg`,
            }}
          />
        );
      })}
    </>
  );
};

type RaysProps = {
  readonly colors: readonly [string, string];
  readonly rays?: number;
  /** Degrees per frame. */
  readonly speed?: number;
  readonly origin?: readonly [number, number];
};

/** Rotating sunburst background from @remotion/effects. */
export const Rays: React.FC<RaysProps> = ({ colors, rays = 22, speed = 0.8, origin = [0.5, 0.45] }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <Solid
      width={width}
      height={height}
      color={colors[0]}
      effects={[starburst({ rays, colors: [colors[0], colors[1]], rotation: (((frame * speed) % 360) + 360) % 360, origin: [origin[0], origin[1]] })]}
    />
  );
};

/** Pop-art halftone dots drawn with CSS. */
export const Halftone: React.FC<{ readonly color?: string; readonly size?: number; readonly drift?: number }> = ({ color = 'rgba(255,255,255,0.09)', size = 30, drift = 0.6 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `radial-gradient(circle, ${color} ${size * 0.16}px, transparent ${size * 0.18}px)`,
        backgroundSize: `${size}px ${size}px`,
        backgroundPosition: `${frame * drift}px ${frame * drift * 1.6}px`,
      }}
    />
  );
};

/** Colour bars that tear across a cut for a few frames; `rising` builds up instead of fading out. */
export const GlitchBurst: React.FC<{ readonly seed: string; readonly frames?: number; readonly rising?: boolean }> = ({ seed, frames = 6, rising = false }) => {
  const frame = useCurrentFrame();
  const strength = rising ? Math.min(1, (frame + 1) / frames) : Math.max(0, 1 - frame / frames);
  if (strength <= 0) return null;
  const colors = [CYAN, HOT, YELLOW, WHITE];
  return (
    <AbsoluteFill style={{ mixBlendMode: 'difference' }}>
      {Array.from({ length: 11 }, (_, i) => {
        const r = (k: string) => random(`${seed}-${frame}-${i}-${k}`);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: -200 + (r('x') - 0.5) * 360 * strength,
              top: r('y') * 1920,
              width: 1480,
              height: 6 + r('h') * r('h') * 200 * strength,
              backgroundColor: colors[Math.floor(r('c') * colors.length)],
              opacity: 0.45 + 0.5 * r('o'),
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
