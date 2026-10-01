import { useCallback } from "react";
import { FILM } from "./pixel/density";
import { PixelFrame } from "./pixel/PixelFrame";
import type { Pix } from "./pixel/pix";
import { drawBoatScene } from "./stills/boatScene";
import { filmAt } from "./storyboard/shots";

// The film at final timing: the storyboard's shots played through on the
// score's bars. The render script adds the score.
export const Animatic: React.FC = () => {
  const draw = useCallback(
    (pix: Pix, frame: number) => drawBoatScene(pix, filmAt(frame).spec, frame),
    [],
  );
  return <PixelFrame density={FILM} draw={draw} />;
};
