import { useLayoutEffect, useMemo } from "react";
import { Color, Mesh, Vector2, Vector3 } from "three";
import { LineBatch, createGlowLineMaterial } from "./glowLine";

// Thin annotation strokes in the glow-line style: a chart's drop lines and markers.

export type Stroke = { points: Vector3[]; color: Color; brightness: number };

type Props = { strokes: Stroke[]; resolution: Vector2; near: number };

export const GuideLines: React.FC<Props> = ({ strokes, resolution, near }) => {
  const { batch, material, mesh } = useMemo(() => {
    const batch = new LineBatch(1024);
    const material = createGlowLineMaterial();
    material.uniforms.uMinPx.value = 5;
    material.uniforms.uWorldWidth.value = 0.02;
    const mesh = new Mesh(batch.geometry, material);
    mesh.frustumCulled = false;
    mesh.renderOrder = 3;
    return { batch, material, mesh };
  }, []);
  useLayoutEffect(() => {
    batch.begin();
    for (const s of strokes) batch.add(s.points, s.points.map(() => s.brightness), s.color);
    batch.end();
    material.uniforms.uResolution.value.copy(resolution);
    material.uniforms.uNear.value = near;
  });
  return <primitive object={mesh} />;
};
