import React from 'react';
import { INK, YELLOW } from '../brand';

type IconProps = {
  readonly size: number;
  readonly color?: string;
  readonly fill?: string;
  readonly style?: React.CSSProperties;
};

const Frame: React.FC<IconProps & { readonly children: React.ReactNode }> = ({ size, color = INK, style, children }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 100 100"
    style={style}
    fill="none"
    stroke={color}
    strokeWidth={8}
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {children}
  </svg>
);

export const PenIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M22 78 L30 56 L70 16 L84 30 L44 70 Z" fill={p.fill} />
    <path d="M22 78 L30 56 L44 70 Z" fill={p.color ?? INK} />
    <path d="M62 24 L76 38" />
  </Frame>
);

export const SparkleIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M50 8 C54 34 66 46 92 50 C66 54 54 66 50 92 C46 66 34 54 8 50 C34 46 46 34 50 8 Z" fill={p.fill} />
    <path d="M82 12 L82 26 M75 19 L89 19" />
  </Frame>
);

export const CameraIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <circle cx="30" cy="26" r="13" fill={p.fill} />
    <circle cx="60" cy="24" r="15" fill={p.fill} />
    <rect x="14" y="42" width="56" height="38" rx="5" fill={p.fill} />
    <path d="M70 52 L90 42 L90 80 L70 70 Z" fill={p.fill} />
  </Frame>
);

export const FilmIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <rect x="18" y="10" width="64" height="80" rx="4" fill={p.fill} />
    <path d="M18 36 L82 36 M18 64 L82 64" />
    {[18, 50, 80].map((y) => (
      <React.Fragment key={y}>
        <rect x="23" y={y - 3} width="5" height="6" fill={p.color ?? INK} stroke="none" />
        <rect x="72" y={y - 3} width="5" height="6" fill={p.color ?? INK} stroke="none" />
      </React.Fragment>
    ))}
  </Frame>
);

export const MicIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <rect x="34" y="8" width="32" height="52" rx="16" fill={p.fill} />
    <path d="M22 46 C22 64 34 74 50 74 C66 74 78 64 78 46" />
    <path d="M50 74 L50 90 M34 92 L66 92" />
  </Frame>
);

export const NoteIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M36 74 L36 22 L80 12 L80 64" />
    <path d="M36 32 L80 22" />
    <ellipse cx="26" cy="76" rx="12" ry="9" fill={p.color ?? INK} />
    <ellipse cx="70" cy="66" rx="12" ry="9" fill={p.color ?? INK} />
  </Frame>
);

export const ScissorsIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <circle cx="24" cy="74" r="12" fill={p.fill} />
    <circle cx="76" cy="74" r="12" fill={p.fill} />
    <path d="M32 64 L72 12 M68 64 L28 12" />
  </Frame>
);

export const RenderIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M50 10 A40 40 0 1 1 14 32" />
    <path d="M40 34 L68 50 L40 66 Z" fill={p.color ?? INK} />
  </Frame>
);

export const CheckIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M16 52 L40 76 L86 24" strokeWidth={14} />
  </Frame>
);

export const ArrowDownIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M50 10 L50 84 M20 56 L50 86 L80 56" strokeWidth={13} />
  </Frame>
);

export const PinIcon: React.FC<IconProps> = (p) => (
  <Frame {...p}>
    <path d="M50 94 C30 66 18 52 18 36 C18 18 32 6 50 6 C68 6 82 18 82 36 C82 52 70 66 50 94 Z" fill={p.fill} />
    <circle cx="50" cy="36" r="12" fill={p.color ?? INK} />
  </Frame>
);

/** Filled warning triangle with an exclamation mark. */
export const WarningIcon: React.FC<{ readonly size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 8 L94 88 L6 88 Z" fill={YELLOW} stroke={INK} strokeWidth={7} strokeLinejoin="round" />
    <path d="M50 36 L50 62" stroke={INK} strokeWidth={10} strokeLinecap="round" />
    <circle cx="50" cy="76" r="6" fill={INK} />
  </svg>
);

/** Round-headed figure for the crowd grid. */
export const PersonIcon: React.FC<{ readonly size: number; readonly color: string }> = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <circle cx="50" cy="30" r="20" fill={color} stroke={INK} strokeWidth={6} />
    <path d="M14 96 C14 66 30 54 50 54 C70 54 86 66 86 96 Z" fill={color} stroke={INK} strokeWidth={6} strokeLinejoin="round" />
  </svg>
);
