import { useLayoutEffect, useMemo } from "react";
import {
  AdditiveBlending,
  Color,
  InstancedBufferAttribute,
  InstancedBufferGeometry,
  BufferAttribute,
  ShaderMaterial,
  Vector2,
  Vector3,
} from "three";

// Camera-facing points of light: a white core, a coloured halo and a thin anamorphic streak.
// Size is the larger of a pixel minimum and a world size, like the lines.

export type Glow = {
  position: Vector3;
  color: Color;
  px: number; // minimum diameter in pixels
  world: number; // diameter in world units
  intensity: number;
  streak?: number; // horizontal streak length, in diameters
  ring?: number; // >0 draws a ring of this relative radius instead of a point
};

const vertexShader = /* glsl */ `
uniform vec2 uResolution;
uniform float uNear;
attribute vec3 iPos;
attribute vec3 iColor;
attribute vec4 iSize; // px, world, intensity, streak
attribute float iRing;
varying vec2 vQ;
varying float vRing;
varying vec3 vColor;
varying float vIntensity;
varying float vStreak;
void main() {
  vec4 vc = viewMatrix * vec4(iPos, 1.0);
  if (vc.z > -uNear) { gl_Position = vec4(0.0, 0.0, 2.0, 1.0); vIntensity = 0.0; return; }
  vec4 cc = projectionMatrix * vc;
  float pxPerUnit = projectionMatrix[1][1] * 0.5 * uResolution.y / -vc.z;
  float px = min(max(iSize.x, iSize.y * pxPerUnit), 900.0);
  float streak = max(1.0, iSize.w);
  vec2 corner = position.xy * vec2(px * 0.5 * streak, px * 0.5);
  cc.xy += corner / (0.5 * uResolution) * cc.w;
  gl_Position = cc;
  vQ = position.xy * vec2(streak, 1.0);
  vColor = iColor;
  vIntensity = iSize.z;
  vStreak = streak;
  vRing = iRing;
}
`;

const fragmentShader = /* glsl */ `
varying vec2 vQ;
varying vec3 vColor;
varying float vIntensity;
varying float vStreak;
varying float vRing;
void main() {
  // Window to zero at the quad's edge so no halo is ever clipped square.
  float wx = 1.0 - pow(vQ.x / vStreak, 2.0);
  float wy = 1.0 - vQ.y * vQ.y;
  float win = clamp(wx, 0.0, 1.0) * clamp(wy, 0.0, 1.0);
  win *= win;
  float r2 = dot(vQ, vQ);
  if (vRing > 0.0) {
    float r = length(vec2(vQ.x / vStreak, vQ.y));
    float ring = exp(-pow((r - vRing) * 14.0, 2.0));
    vec3 col = mix(vColor, vec3(1.0), 0.35) * ring * win;
    gl_FragColor = vec4(col * vIntensity, 1.0);
    return;
  }
  float halo = exp(-r2 * 5.0);
  float core = exp(-r2 * 70.0);
  float line = exp(-vQ.y * vQ.y * 1400.0) * exp(-abs(vQ.x) * 4.0 / vStreak) * step(1.01, vStreak);
  vec3 col = vColor * halo * 0.7 + mix(vColor, vec3(1.0), 0.8) * core * 3.0 + mix(vColor, vec3(1.0), 0.4) * line * 0.5;
  gl_FragColor = vec4(col * vIntensity * win, 1.0);
}
`;

export const Glows: React.FC<{ glows: Glow[]; resolution: Vector2; near: number; capacity?: number }> = ({
  glows,
  resolution,
  near,
  capacity = 4096,
}) => {
  const { geometry, material, pos, col, size, ring } = useMemo(() => {
    const geometry = new InstancedBufferGeometry();
    geometry.setAttribute(
      "position",
      new BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]), 3),
    );
    geometry.setIndex([0, 1, 2, 0, 2, 3]);
    const pos = new InstancedBufferAttribute(new Float32Array(capacity * 3), 3);
    const col = new InstancedBufferAttribute(new Float32Array(capacity * 3), 3);
    const size = new InstancedBufferAttribute(new Float32Array(capacity * 4), 4);
    const ring = new InstancedBufferAttribute(new Float32Array(capacity), 1);
    geometry.setAttribute("iPos", pos);
    geometry.setAttribute("iColor", col);
    geometry.setAttribute("iSize", size);
    geometry.setAttribute("iRing", ring);
    const material = new ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: { uResolution: { value: new Vector2() }, uNear: { value: 0.05 } },
      transparent: true,
      depthWrite: false,
      blending: AdditiveBlending,
    });
    return { geometry, material, pos, col, size, ring };
  }, [capacity]);

  useLayoutEffect(() => {
    const n = Math.min(glows.length, capacity);
    for (let i = 0; i < n; i++) {
      const g = glows[i];
      pos.setXYZ(i, g.position.x, g.position.y, g.position.z);
      col.setXYZ(i, g.color.r, g.color.g, g.color.b);
      size.setXYZW(i, g.px, g.world, g.intensity, g.streak ?? 1);
      ring.setX(i, g.ring ?? 0);
    }
    pos.needsUpdate = true;
    col.needsUpdate = true;
    size.needsUpdate = true;
    ring.needsUpdate = true;
    geometry.instanceCount = n;
    material.uniforms.uResolution.value.copy(resolution);
    material.uniforms.uNear.value = near;
  });

  return <mesh geometry={geometry} material={material} frustumCulled={false} renderOrder={5} />;
};
