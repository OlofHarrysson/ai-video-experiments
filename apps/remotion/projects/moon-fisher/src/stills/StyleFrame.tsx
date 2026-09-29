import { useCallback } from "react";
import { FILM } from "../pixel/density";
import { PixelFrame } from "../pixel/PixelFrame";
import type { Pix } from "../pixel/pix";
import { drawBoatScene } from "./boatScene";
import { specAt, type SceneName } from "./scenes";

export const SceneFrame: React.FC<{ scene: SceneName }> = ({ scene }) => {
  const draw = useCallback(
    (pix: Pix, frame: number) =>
      drawBoatScene(pix, specAt(scene, frame), frame),
    [scene],
  );
  return <PixelFrame density={FILM} draw={draw} />;
};
