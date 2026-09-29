import { Composition, Folder, Still } from "remotion";
import { StyleFrame } from "./stills/StyleFrame";

export const FPS = 24;

export const RemotionRoot: React.FC = () => (
  <Folder name="Style-frame">
    <Still
      id="StyleFrameA"
      component={StyleFrame}
      width={1080}
      height={1920}
      defaultProps={{ density: "A" as const }}
    />
    <Still
      id="StyleFrameB"
      component={StyleFrame}
      width={1080}
      height={1920}
      defaultProps={{ density: "B" as const }}
    />
    <Composition
      id="StyleLoopB"
      component={StyleFrame}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={FPS * 4}
      defaultProps={{ density: "B" as const }}
    />
  </Folder>
);
