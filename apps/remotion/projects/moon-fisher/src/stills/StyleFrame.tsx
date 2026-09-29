import { FILM } from "../pixel/density";
import { PixelFrame } from "../pixel/PixelFrame";
import { drawKeyImage } from "./keyImage";

export const StyleFrame: React.FC = () => (
  <PixelFrame density={FILM} draw={drawKeyImage} />
);
