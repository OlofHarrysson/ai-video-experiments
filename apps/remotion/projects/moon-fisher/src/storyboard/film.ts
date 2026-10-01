import { bayer, Pix } from "../pixel/pix";
import { drawBoatScene } from "../stills/boatScene";
import { filmAt } from "./shots";

// A frame of the film. Where a shot dissolves in, the shot before it shows
// through an ordered-dither mask that clears as the dissolve goes on.
export const drawFilm = (pix: Pix, frame: number): void => {
  const { spec, from } = filmAt(frame);
  drawBoatScene(pix, spec, frame);
  if (!from) return;
  const before = new Pix(pix.w, pix.h, pix.k);
  drawBoatScene(before, from.spec, frame);
  for (let py = 0; py < pix.h; py++) {
    for (let px = 0; px < pix.w; px++) {
      if (bayer(px, py) < from.mix) continue;
      const i = py * pix.w + px;
      pix.data[i] = before.data[i];
    }
  }
};
