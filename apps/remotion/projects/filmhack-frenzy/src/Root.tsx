import './fonts';
import React from 'react';
import { Composition, Folder } from 'remotion';
import { FilmhackFrenzy } from './FilmhackFrenzy';
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
import { DURATION_IN_FRAMES, FPS, sceneFrames, type SceneName } from './timing';

const SCENE_COMPONENTS: [SceneName, string, React.FC][] = [
  ['coldOpen', 'ColdOpen', ColdOpen],
  ['stopScrolling', 'StopScrolling', StopScrolling],
  ['lightsCameraAction', 'LightsCameraAction', LightsCameraAction],
  ['prompts', 'Prompts', Prompts],
  ['pipeline', 'Pipeline', Pipeline],
  ['crowd', 'Crowd', Crowd],
  ['chaos', 'Chaos', Chaos],
  ['sunday', 'Sunday', Sunday],
  ['premiere', 'Premiere', Premiere],
  ['facts', 'Facts', Facts],
  ['cta', 'CallToAction', Cta],
];

// Durations follow the 150 BPM grid in timing.ts, which the score shares.
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="FilmhackFrenzy" component={FilmhackFrenzy} durationInFrames={DURATION_IN_FRAMES} fps={FPS} width={1080} height={1920} />
    <Folder name="Frenzy-Scenes">
      {SCENE_COMPONENTS.map(([scene, id, component]) => (
        <Composition key={id} id={id} component={component} durationInFrames={sceneFrames(scene)} fps={FPS} width={1080} height={1920} />
      ))}
    </Folder>
  </>
);
