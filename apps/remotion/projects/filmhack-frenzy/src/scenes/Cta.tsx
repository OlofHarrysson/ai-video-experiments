import { useWindowedAudioData, visualizeAudio } from '@remotion/media-utils';
import React from 'react';
import { AbsoluteFill, Interactive, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { INK, MONO, RED, WHITE, YELLOW } from '../brand';
import { Confetti, GlitchBurst, Halftone, Rays, Sticker, Tape } from '../components/decor';
import { ArrowDownIcon } from '../components/icons';
import { beatPulse, decayFrom, Punch, Shake, Slam } from '../components/motion';
import { beat, SCENES } from '../timing';

const FINAL = beat(10);

/** Kick-reactive pulse for the button, read from the soundtrack itself. */
const useBass = (globalFrame: number) => {
  const { fps } = useVideoConfig();
  const { audioData, dataOffsetInSeconds } = useWindowedAudioData({ src: staticFile('soundtrack.wav'), frame: globalFrame, fps, windowInSeconds: 10 });
  if (!audioData) return 0;
  const bins = visualizeAudio({ fps, frame: globalFrame, audioData, numberOfSamples: 32, optimizeFor: 'speed', dataOffsetInSeconds });
  return Math.min(1, (bins[0] + bins[1] + bins[2]) * 1.2);
};

/** Beats 52–64: GET ON THE LIST, the link, the final hit, then a glitch back into the loop. */
export const Cta: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const bass = useBass(beat(SCENES.cta[0]) + frame);
  const pop = spring({ frame: frame - beat(2), fps, config: { damping: 9, stiffness: 200, mass: 0.6 } });
  const hop = 26 * beatPulse(frame, 4);
  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: 'hidden' }}>
      <Rays colors={['#0A0A0A', '#151515']} rays={24} speed={1.2} />
      <Halftone color="rgba(255,212,0,0.08)" />
      <Shake amount={3 + 12 * decayFrom(frame, [0, 6, FINAL]) + 6 * decayFrom(frame, [beat(8), beat(9)])} seed="cta">
        <Punch hits={[0, 6, FINAL]} amount={0.06}>
          <Tape y={190} angle={-6} speed={10} text="AI FILMHACK • GET ON THE LIST • " />
          <Tape y={1660} angle={5} speed={-10} text="NOV 12–15 • POTSDAM • FREE • 100 SPOTS • " />
          <Slam at={0} rotate={-4} style={{ left: 0, right: 0, top: 320, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div name="GET ON" style={{ fontFamily: 'MangoGrotesque', fontSize: 290, lineHeight: 1, color: '#FFFFFF', filter: 'drop-shadow(12px 12px 0 #C80528)' }}>
              GET ON
            </Interactive.Div>
          </Slam>
          <Slam at={6} rotate={3} from={2.3} style={{ left: 0, right: 0, top: 580, display: 'flex', justifyContent: 'center' }}>
            <Interactive.Div
              name="THE LIST"
              style={{ fontFamily: 'MangoGrotesque', fontSize: 330, lineHeight: 1, color: '#FFD400', WebkitTextStroke: '8px #0A0A0A', paintOrder: 'stroke fill', filter: 'drop-shadow(14px 14px 0 #FF1E50)' }}
            >
              THE LIST!
            </Interactive.Div>
          </Slam>
          {frame >= beat(2) ? (
            <div
              style={{
                position: 'absolute',
                left: 90,
                top: 990,
                width: 900,
                height: 170,
                scale: String(pop * (1 + 0.05 * bass)),
                rotate: '-2deg',
                backgroundColor: RED,
                border: `9px solid ${INK}`,
                borderRadius: 28,
                boxShadow: `16px 16px 0 ${YELLOW}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: MONO,
                fontWeight: 700,
                fontSize: 78,
                letterSpacing: 4,
                color: WHITE,
                textShadow: 'none',
              }}
            >
              FILMHACK.AI →
            </div>
          ) : null}
          <Sequence from={beat(3)} layout="none">
            <Slam at={0} style={{ left: 0, right: 0, top: 1215, display: 'flex', justifyContent: 'center' }}>
              <Interactive.Div name="LINK IN BIO" style={{ fontFamily: 'MangoGrotesque', fontSize: 130, lineHeight: 1, color: '#FFFFFF' }}>
                LINK IN BIO
              </Interactive.Div>
            </Slam>
            <div style={{ position: 'absolute', left: 60, top: 1200, translate: `0px ${hop}px` }}>
              <ArrowDownIcon size={120} color={YELLOW} />
            </div>
            <div style={{ position: 'absolute', right: 60, top: 1200, translate: `0px ${hop}px` }}>
              <ArrowDownIcon size={120} color={YELLOW} />
            </div>
          </Sequence>
          <Sticker at={beat(4)} x={950} y={300} size={190} color="#00E08A" angle={14}>
            FREE!
          </Sticker>
          <Sticker at={beat(4.5)} x={130} y={880} size={180} color="#00D2E6" angle={-12} spin={-1.3}>
            NOV
            <br />
            12–15
          </Sticker>
          <Sticker at={beat(5)} x={950} y={880} size={180} color="#FF1E50" ink={WHITE} angle={10}>
            100
            <br />
            SPOTS
          </Sticker>
          <Confetti at={FINAL} x={540} y={1300} seed="final-c" count={130} power={2800} spread={200} />
          <Confetti at={FINAL} x={60} y={1900} seed="final-l" direction={25} spread={40} power={3300} count={70} />
          <Confetti at={FINAL} x={1020} y={1900} seed="final-r" direction={-25} spread={40} power={3300} count={70} />
        </Punch>
      </Shake>
      <Sequence from={beat(11.3)} layout="none">
        <GlitchBurst seed="loop" frames={8} rising />
      </Sequence>
    </AbsoluteFill>
  );
};
