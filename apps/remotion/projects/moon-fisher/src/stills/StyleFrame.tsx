import { DENSITIES, type DensityName } from "../pixel/density";
import { PixelFrame } from "../pixel/PixelFrame";
import { drawKeyImage } from "./keyImage";

export const StyleFrame: React.FC<{ density: DensityName }> = ({ density }) => (
  <PixelFrame density={DENSITIES[density]} draw={drawKeyImage} />
);
