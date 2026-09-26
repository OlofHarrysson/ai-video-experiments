import { fitText } from '@remotion/layout-utils';
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { CYAN, DISPLAY, INK, MONO, RED, WHITE, YELLOW } from '../brand';
import { Countdown } from '../components/Countdown';
import { Rays } from '../components/decor';
import { CameraIcon, FilmIcon, MicIcon, NoteIcon, PenIcon, RenderIcon, ScissorsIcon, SparkleIcon } from '../components/icons';
import { decayFrom, Shake, Slam } from '../components/motion';
import { beat, SCENES } from '../timing';

const WORDS = [
  { word: 'WRITE!', Icon: PenIcon },
  { word: 'PROMPT!', Icon: SparkleIcon },
  { word: 'SHOOT!', Icon: CameraIcon },
  { word: 'ANIMATE!', Icon: FilmIcon },
  { word: 'VOICE!', Icon: MicIcon },
  { word: 'SCORE!', Icon: NoteIcon },
  { word: 'CUT!', Icon: ScissorsIcon },
  { word: 'RENDER!', Icon: RenderIcon },
];

/** Background only changes on the beat (2.5 times a second) to stay clear of flashing thresholds. */
const BEATS = [
  { bg: YELLOW, ray: '#F5C800', ink: INK, badge: WHITE },
  { bg: CYAN, ray: '#00C2D6', ink: INK, badge: YELLOW },
  { bg: RED, ray: '#B30424', ink: WHITE, badge: INK },
  { bg: INK, ray: '#171717', ink: YELLOW, badge: RED },
];

const EIGHTH = beat(0.5);

/** Beats 16–20: the whole pipeline, one word per eighth note. */
export const Pipeline: React.FC = () => {
  const frame = useCurrentFrame();
  const index = Math.min(WORDS.length - 1, Math.floor(frame / EIGHTH));
  const look = BEATS[Math.min(BEATS.length - 1, Math.floor(frame / beat(1)))];
  const { word, Icon } = WORDS[index];
  const hit = decayFrom(frame, [index * EIGHTH], 2.5);
  const fontSize = Math.min(360, fitText({ text: word, withinWidth: 900, fontFamily: DISPLAY }).fontSize);
  const iconColor = look.badge === INK ? WHITE : INK;
  return (
    <AbsoluteFill style={{ backgroundColor: look.bg, overflow: 'hidden' }}>
      <Rays colors={[look.bg, look.ray]} rays={18} speed={3} origin={[0.5, 0.36]} />
      <Shake amount={5 + 22 * hit} seed="pipeline">
        <Countdown globalFrame={beat(SCENES.pipeline[0]) + frame} x={240} y={210} width={600} />
        <div
          style={{
            position: 'absolute',
            left: 540 - 150,
            top: 510,
            width: 300,
            height: 300,
            borderRadius: '50%',
            backgroundColor: look.badge,
            border: `9px solid ${INK}`,
            boxShadow: `14px 14px 0 ${INK}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            translate: `0px ${-40 * hit}px`,
            rotate: `${(index % 2 ? 8 : -8) * (1 - hit)}deg`,
          }}
        >
          <Icon size={190} color={iconColor} fill={look.bg === INK ? RED : WHITE} />
        </div>
        <Slam key={index} at={index * EIGHTH} rotate={index % 2 ? 4 : -4} from={1.6} style={{ left: 0, right: 0, top: 880, display: 'flex', justifyContent: 'center' }}>
          <div style={{ color: look.ink, fontFamily: DISPLAY, fontSize, lineHeight: 1, filter: `drop-shadow(12px 12px 0 ${look.bg === INK ? RED : INK})` }}>{word}</div>
        </Slam>
        <div style={{ position: 'absolute', left: 0, right: 0, top: 1330, display: 'flex', justifyContent: 'center', gap: 18 }}>
          {WORDS.map((w, i) => (
            <div key={w.word} style={{ width: i === index ? 64 : 26, height: 26, borderRadius: 13, backgroundColor: i <= index ? look.ink : 'rgba(10,10,10,0.18)', border: `4px solid ${look.ink}` }} />
          ))}
        </div>
        <div style={{ position: 'absolute', left: 0, right: 0, top: 1400, textAlign: 'center', fontFamily: MONO, fontWeight: 700, fontSize: 40, letterSpacing: 6, color: look.ink, textShadow: 'none' }}>
          {String(index + 1).padStart(2, '0')} / 08 · IDEA TO SCREEN
        </div>
      </Shake>
    </AbsoluteFill>
  );
};

