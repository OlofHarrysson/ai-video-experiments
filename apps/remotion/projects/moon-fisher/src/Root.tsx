import { Composition, Folder, Still } from "remotion";
import { StyleFrame } from "./stills/StyleFrame";

export const FPS = 24;

export const RemotionRoot: React.FC = () => (
  <Folder name="Style-frame">
    <Still id="StyleFrame" component={StyleFrame} width={1080} height={1920} />
    <Composition
      id="StyleLoop"
      component={StyleFrame}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 4}
    />
  </Folder>
);
