import { useThree } from "@react-three/fiber";
import { useLayoutEffect } from "react";
import { PerspectiveCamera } from "three";
import { Shot } from "../camera";

export const CameraRig: React.FC<{ shot: Shot; near: number; far: number }> = ({ shot, near, far }) => {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  useLayoutEffect(() => {
    camera.position.copy(shot.position);
    camera.up.set(0, 1, 0);
    camera.lookAt(shot.target);
    camera.rotateZ(shot.roll);
    camera.fov = shot.fov;
    camera.near = near;
    camera.far = far;
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld(true);
  });
  return null;
};
