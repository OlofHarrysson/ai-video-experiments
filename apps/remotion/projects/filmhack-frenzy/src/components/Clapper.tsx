import React from 'react';
import { CYAN, DISPLAY, INK, MONO, WHITE } from '../brand';

const stripes = (y: number, h: number, dir: 1 | -1) =>
  Array.from({ length: 9 }, (_, i) => {
    const x = -40 + i * 56;
    const slant = h * 1.1 * dir;
    return <polygon key={i} points={`${x},${y + h} ${x + 26},${y + h} ${x + 26 + slant},${y} ${x + slant},${y}`} fill={INK} />;
  });

/** Clapperboard in the site's slate style. `arm` is the arm angle in degrees; negative opens it. */
export const Clapper: React.FC<{ readonly width: number; readonly arm: number }> = ({ width, arm }) => (
  <svg width={width} height={width * 0.86} viewBox="0 -20 400 344" style={{ overflow: 'visible' }}>
    <g transform={`rotate(${arm} 6 92)`}>
      <rect x="0" y="54" width="400" height="38" fill={WHITE} stroke={INK} strokeWidth="4" />
      <clipPath id="arm-clip">
        <rect x="0" y="54" width="400" height="38" />
      </clipPath>
      <g clipPath="url(#arm-clip)">{stripes(54, 38, 1)}</g>
    </g>
    <rect x="0" y="92" width="400" height="34" fill={WHITE} stroke={INK} strokeWidth="4" />
    <clipPath id="stick-clip">
      <rect x="0" y="92" width="400" height="34" />
    </clipPath>
    <g clipPath="url(#stick-clip)">{stripes(92, 34, -1)}</g>
    <circle cx="8" cy="92" r="6" fill="#9a9a9a" />
    <rect x="0" y="126" width="400" height="196" fill="#0d0d0d" stroke="#2c2c2c" strokeWidth="4" />
    <path d="M0 196 H400 M0 262 H400 M200 196 V262" stroke="#2c2c2c" strokeWidth="3" />
    <text x="16" y="146" fontFamily={MONO} fontWeight={700} fontSize="13" fill="rgba(255,255,255,0.45)" letterSpacing="2">
      PROD.
    </text>
    <text x="16" y="186" fontFamily={DISPLAY} fontSize="44" fill={WHITE}>
      AI FILMHACK
    </text>
    <text x="16" y="216" fontFamily={MONO} fontWeight={700} fontSize="13" fill="rgba(255,255,255,0.45)" letterSpacing="2">
      SCENE
    </text>
    <text x="16" y="248" fontFamily={MONO} fontWeight={700} fontSize="26" fill={WHITE}>
      01
    </text>
    <text x="216" y="216" fontFamily={MONO} fontWeight={700} fontSize="13" fill="rgba(255,255,255,0.45)" letterSpacing="2">
      TAKE
    </text>
    <text x="216" y="248" fontFamily={MONO} fontWeight={700} fontSize="26" fill={WHITE}>
      01
    </text>
    <text x="16" y="282" fontFamily={MONO} fontWeight={700} fontSize="13" fill="rgba(255,255,255,0.45)" letterSpacing="2">
      DIRECTOR
    </text>
    <text x="16" y="312" fontFamily={MONO} fontWeight={700} fontSize="26" fill={CYAN}>
      YOU
    </text>
  </svg>
);
