import { Composition, Folder, Still } from "remotion";
import { SceneFrame } from "./stills/StyleFrame";

export const FPS = 24;

const SIZE = { width: 1080, height: 1920 };

export const RemotionRoot: React.FC = () => (
  <>
    <Folder name="Style-frame">
      <Still
        id="StyleFrame"
        component={SceneFrame}
        {...SIZE}
        defaultProps={{ scene: "key" as const }}
      />
      <Composition
        id="StyleLoop"
        component={SceneFrame}
        {...SIZE}
        fps={FPS}
        durationInFrames={FPS * 4}
        defaultProps={{ scene: "key" as const }}
      />
    </Folder>
    <Folder name="Poses">
      <Still
        id="PoseDoze"
        component={SceneFrame}
        {...SIZE}
        defaultProps={{ scene: "doze" as const }}
      />
      <Still
        id="PoseHaul"
        component={SceneFrame}
        {...SIZE}
        defaultProps={{ scene: "haul" as const }}
      />
      <Still
        id="PoseTip"
        component={SceneFrame}
        {...SIZE}
        defaultProps={{ scene: "tip" as const }}
      />
      <Composition
        id="HaulTest"
        component={SceneFrame}
        {...SIZE}
        fps={FPS}
        durationInFrames={FPS * 3}
        defaultProps={{ scene: "haulTest" as const }}
      />
    </Folder>
  </>
);
