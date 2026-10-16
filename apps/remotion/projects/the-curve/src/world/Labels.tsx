import { useLayoutEffect, useMemo } from "react";
import {
  BufferAttribute,
  CustomBlending,
  InstancedBufferAttribute,
  InstancedBufferGeometry,
  OneFactor,
  OneMinusSrcAlphaFactor,
  ShaderMaterial,
  Texture,
  Vector2,
  Vector3,
} from "three";
import { Atlas } from "../text/atlas";

// Camera-facing text from the atlas. Height is the larger of a pixel minimum and a world height
// (capped), so labels live in the world but stay legible.

export type Label = {
  key: string;
  position: Vector3;
  minPx: number;
  world: number;
  maxPx?: number;
  color: [number, number, number]; // multiplies the atlas colour; >1 glows
  opacity: number;
  offset?: [number, number]; // anchor shift in label heights (x, y)
  rotation?: number; // in-plane rotation, radians
};

const vertexShader = /* glsl */ `
uniform vec2 uResolution;
uniform float uNear;
attribute vec3 iPos;
attribute vec4 iRect;
attribute vec4 iSize;   // minPx, world, aspect, maxPx
attribute vec4 iColor;  // rgb, opacity
attribute vec3 iOffset; // offset x, offset y (in heights), rotation
varying vec2 vUv;
varying vec4 vColor;
void main() {
  vec4 vc = viewMatrix * vec4(iPos, 1.0);
  if (vc.z > -uNear) { gl_Position = vec4(0.0, 0.0, 2.0, 1.0); vColor = vec4(0.0); return; }
  vec4 cc = projectionMatrix * vc;
  float pxPerUnit = projectionMatrix[1][1] * 0.5 * uResolution.y / -vc.z;
  float h = clamp(iSize.y * pxPerUnit, iSize.x, iSize.w);
  float w = h * iSize.z;
  vec2 local = (position.xy * 0.5 + iOffset.xy * vec2(1.0, 1.0)) * vec2(w, h);
  float c = cos(iOffset.z);
  float s = sin(iOffset.z);
  local = vec2(c * local.x - s * local.y, s * local.x + c * local.y);
  cc.xy += local / (0.5 * uResolution) * cc.w;
  gl_Position = cc;
  vUv = mix(iRect.xy, iRect.zw, position.xy * 0.5 + 0.5);
  vColor = iColor;
}
`;

const fragmentShader = /* glsl */ `
uniform sampler2D uAtlas;
varying vec2 vUv;
varying vec4 vColor;
void main() {
  vec4 tex = texture2D(uAtlas, vUv);
  float a = tex.a * vColor.a;
  gl_FragColor = vec4(tex.rgb * vColor.rgb * a, a);
}
`;

type Props = { atlas: Atlas; labels: Label[]; resolution: Vector2; near: number; additive?: boolean; capacity?: number };

export const Labels: React.FC<Props> = ({ atlas, labels, resolution, near, additive = false, capacity = 2048 }) => {
  const { geometry, material, attrs } = useMemo(() => {
    const geometry = new InstancedBufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]), 3));
    geometry.setIndex([0, 1, 2, 0, 2, 3]);
    const attrs = {
      pos: new InstancedBufferAttribute(new Float32Array(capacity * 3), 3),
      rect: new InstancedBufferAttribute(new Float32Array(capacity * 4), 4),
      size: new InstancedBufferAttribute(new Float32Array(capacity * 4), 4),
      color: new InstancedBufferAttribute(new Float32Array(capacity * 4), 4),
      offset: new InstancedBufferAttribute(new Float32Array(capacity * 3), 3),
    };
    geometry.setAttribute("iPos", attrs.pos);
    geometry.setAttribute("iRect", attrs.rect);
    geometry.setAttribute("iSize", attrs.size);
    geometry.setAttribute("iColor", attrs.color);
    geometry.setAttribute("iOffset", attrs.offset);
    const material = new ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uResolution: { value: new Vector2() },
        uNear: { value: 0.05 },
        uAtlas: { value: null as Texture | null },
      },
      transparent: true,
      depthWrite: false,
      depthTest: true,
      blending: CustomBlending,
      blendSrc: OneFactor,
      blendDst: additive ? OneFactor : OneMinusSrcAlphaFactor,
    });
    return { geometry, material, attrs };
  }, [capacity, additive]);

  useLayoutEffect(() => {
    let n = 0;
    for (const l of labels) {
      if (n >= capacity) break;
      const e = atlas.entries.get(l.key);
      if (!e || l.opacity <= 0.001) continue;
      attrs.pos.setXYZ(n, l.position.x, l.position.y, l.position.z);
      attrs.rect.setXYZW(n, e.u0, e.v0, e.u1, e.v1);
      attrs.size.setXYZW(n, l.minPx, l.world, e.aspect, l.maxPx ?? 400);
      attrs.color.setXYZW(n, l.color[0], l.color[1], l.color[2], l.opacity);
      attrs.offset.setXYZ(n, l.offset?.[0] ?? 0, l.offset?.[1] ?? 0, l.rotation ?? 0);
      n++;
    }
    for (const a of Object.values(attrs)) a.needsUpdate = true;
    geometry.instanceCount = n;
    material.uniforms.uResolution.value.copy(resolution);
    material.uniforms.uNear.value = near;
    material.uniforms.uAtlas.value = atlas.texture;
  });

  return <mesh geometry={geometry} material={material} frustumCulled={false} renderOrder={8} />;
};
