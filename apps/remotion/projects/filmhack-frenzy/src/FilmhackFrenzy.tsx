import { Audio } from '@remotion/media';
import { TransitionSeries } from '@remotion/transitions';
import React from 'react';
import { AbsoluteFill, staticFile } from 'remotion';
import { GlitchBurst } from './components/decor';
import { Chaos } from './scenes/Chaos';
import { ColdOpen } from './scenes/ColdOpen';
import { Crowd } from './scenes/Crowd';
import { Cta } from './scenes/Cta';
import { Facts } from './scenes/Facts';
import { LightsCameraAction } from './scenes/LightsCameraAction';
import { Pipeline } from './scenes/Pipeline';
import { Premiere } from './scenes/Premiere';
import { Prompts } from './scenes/Prompts';
import { StopScrolling } from './scenes/StopScrolling';
import { Sunday } from './scenes/Sunday';
import { FPS, sceneFrames } from './timing';

/** Glitch bars tearing across a hard cut, starting on the downbeat. */
const Cut: React.FC<{ readonly seed: string }> = ({ seed }) => <GlitchBurst seed={seed} frames={5} />;

/**
 * The frenzy cut. Scene lengths come from the beat grid the score is written on,
 * so every cut lands on the music; overlays add glitches without shifting any cut.
 */
export const FilmhackFrenzy: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: '#0A0A0A' }}>
    <TransitionSeries>
      <TransitionSeries.Sequence name="Cold open" durationInFrames={sceneFrames('coldOpen')} premountFor={FPS}>
        <ColdOpen />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-stop" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Stop scrolling" durationInFrames={sceneFrames('stopScrolling')} premountFor={FPS}>
        <StopScrolling />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-action" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Lights camera action" durationInFrames={sceneFrames('lightsCameraAction')} premountFor={FPS}>
        <LightsCameraAction />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-prompts" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Prompts" durationInFrames={sceneFrames('prompts')} premountFor={FPS}>
        <Prompts />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-pipeline" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Pipeline" durationInFrames={sceneFrames('pipeline')} premountFor={FPS}>
        <Pipeline />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-crowd" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Crowd" durationInFrames={sceneFrames('crowd')} premountFor={FPS}>
        <Crowd />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-chaos" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Chaos" durationInFrames={sceneFrames('chaos')} premountFor={FPS}>
        <Chaos />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="Sunday" durationInFrames={sceneFrames('sunday')} premountFor={FPS}>
        <Sunday />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-premiere" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Premiere" durationInFrames={sceneFrames('premiere')} premountFor={FPS}>
        <Premiere />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-facts" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Facts" durationInFrames={sceneFrames('facts')} premountFor={FPS}>
        <Facts />
      </TransitionSeries.Sequence>
      <TransitionSeries.Overlay durationInFrames={5} offset={3}>
        <Cut seed="cut-cta" />
      </TransitionSeries.Overlay>
      <TransitionSeries.Sequence name="Call to action" durationInFrames={sceneFrames('cta')} premountFor={FPS}>
        <Cta />
      </TransitionSeries.Sequence>
    </TransitionSeries>
    <Audio src={staticFile('soundtrack.wav')} />
  </AbsoluteFill>
);
