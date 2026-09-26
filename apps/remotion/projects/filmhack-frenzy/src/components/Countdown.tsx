import React from 'react';
import { CYAN, HOT, MONO, SEG } from '../brand';
import { CLOCK_START_BEAT, CLOCK_ZERO_BEAT, FRAMES_PER_BEAT } from '../timing';

const HOURS_48 = 48 * 3600;

/** Seconds left on the 48-hour clock, racing faster as the montage builds. */
export const remainingAt = (globalFrame: number) => {
  const beat = globalFrame / FRAMES_PER_BEAT;
  const v = Math.min(1, Math.max(0, (beat - CLOCK_START_BEAT) / (CLOCK_ZERO_BEAT - CLOCK_START_BEAT)));
  return HOURS_48 * (1 - Math.pow(v, 1.5));
};

const pad = (n: number) => String(n).padStart(2, '0');

export const hms = (seconds: number) => {
  const s = Math.max(0, Math.floor(seconds));
  return `${pad(Math.floor(s / 3600))}:${pad(Math.floor((s % 3600) / 60))}:${pad(s % 60)}`;
};

type CountdownProps = {
  readonly globalFrame: number;
  readonly x: number;
  readonly y: number;
  readonly width: number;
};

/** The site's "ROLLING IN" countdown panel. Turns red and blinks at zero. */
export const Countdown: React.FC<CountdownProps> = ({ globalFrame, x, y, width }) => {
  const k = width / 900;
  const seconds = remainingAt(globalFrame);
  const done = seconds <= 0;
  const blinkOn = done ? globalFrame % 6 < 3 : globalFrame % FRAMES_PER_BEAT < 7;
  const color = done ? HOT : CYAN;
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height: 300 * k,
        backgroundColor: '#070707',
        border: `${3 * k}px solid #262626`,
        boxShadow: `0 ${14 * k}px 0 rgba(0,0,0,0.5)`,
        textShadow: 'none',
      }}
    >
      <div style={{ position: 'absolute', left: 30 * k, top: 22 * k, fontFamily: MONO, fontWeight: 700, fontSize: 26 * k, letterSpacing: 3 * k, color: blinkOn ? HOT : 'rgba(255,30,80,0.3)' }}>
        ■ ROLLING
      </div>
      <div style={{ position: 'absolute', right: 30 * k, top: 22 * k, fontFamily: MONO, fontWeight: 700, fontSize: 26 * k, letterSpacing: 3 * k, color: 'rgba(255,255,255,0.55)' }}>
        48H FILM CLOCK
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 78 * k, textAlign: 'center', fontFamily: SEG, fontSize: 168 * k, lineHeight: 1 }}>
        <span style={{ position: 'absolute', left: 0, right: 0, color: done ? 'rgba(255,30,80,0.1)' : 'rgba(0,210,230,0.09)' }}>88:88:88</span>
        <span style={{ position: 'relative', color, opacity: done && !blinkOn ? 0.15 : 1, textShadow: `0 0 ${26 * k}px ${color}` }}>{hms(seconds)}</span>
      </div>
    </div>
  );
};
