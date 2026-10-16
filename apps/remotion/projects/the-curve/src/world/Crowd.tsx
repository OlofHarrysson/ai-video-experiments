import { useLayoutEffect, useMemo } from "react";
import { InstancedMesh, Matrix4, Quaternion, ShaderMaterial, Vector3 } from "three";
import { hash } from "../lib/math";
import { buildFigure, createFigureMaterial } from "./Figure";

// Everyone else: thousands of people on the plain, all turned toward the column, heads tipped back.

type Props = { cam: Vector3; light: Vector3; focus: Vector3; count?: number; reveal: number };

export const Crowd: React.FC<Props> = ({ cam, light, focus, count = 3200, reveal }) => {
  const mesh = useMemo(() => {
    const m = new InstancedMesh(buildFigure(1), createFigureMaterial(), count);
    m.frustumCulled = false;
    const q = new Quaternion();
    const up = new Vector3(0, 1, 0);
    const m4 = new Matrix4();
    let placed = 0;
    for (let i = 0; placed < count && i < count * 6; i++) {
      const r = (n: number) => hash(i, n, 313);
      const z = -18 + Math.pow(r(1), 0.9) * 58;
      const spread = 16 + (z + 18) * 1.0;
      const x = (r(2) - 0.5) * 2 * spread;
      // Nobody inside the opening framing, so the pull-back is what reveals them; keep the hero,
      // the camera's path and the race's floor line clear.
      if (z < 9.4 && Math.abs(x - 1.2) < (9.4 - z) * 0.5 + 1.2) continue;
      if (Math.hypot(x + 0.45, z) < 2.6) continue;
      if (Math.abs(x - 3.5) < 2.2 && z > 0) continue;
      const dx = focus.x - x;
      const dz = focus.z - z;
      q.setFromAxisAngle(up, Math.atan2(-dx, -dz) + (r(3) - 0.5) * 0.25);
      const s = 0.86 + r(4) * 0.26;
      const wide = 0.9 + r(5) * 0.25;
      m4.compose(new Vector3(x, 0, z), q, new Vector3(s * wide, s, s * wide));
      m.setMatrixAt(placed, m4);
      placed++;
    }
    m.count = placed;
    m.instanceMatrix.needsUpdate = true;
    return m;
  }, [count, focus]);

  useLayoutEffect(() => {
    const mat = mesh.material as ShaderMaterial;
    mat.uniforms.uCam.value.copy(cam);
    mat.uniforms.uLight.value.copy(light);
    mat.uniforms.uRimStrength.value = 1.5 * reveal;
  });

  return <primitive object={mesh} />;
};
