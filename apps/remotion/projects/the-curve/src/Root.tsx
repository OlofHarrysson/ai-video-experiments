import { Composition } from "remotion";
import { TheCurve } from "./TheCurve";
import { DURATION_FRAMES, FPS, HEIGHT, WIDTH } from "./timing";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="TheCurve"
    component={TheCurve}
    durationInFrames={DURATION_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
