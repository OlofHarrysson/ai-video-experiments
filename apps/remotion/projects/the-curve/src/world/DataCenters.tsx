import { useLayoutEffect, useMemo } from "react";
import {
  BoxGeometry,
  Color,
  InstancedBufferAttribute,
  InstancedMesh,
  Matrix4,
  ShaderMaterial,
  Vector3,
} from "three";
import { PALETTE } from "../palette";
import { Mapping, timeAtS } from "../race";
import { hash } from "../lib/math";

// Campuses of low, wide halls along the race. Each one is built in place: a glowing wireframe
// rises, the shell closes, then rows of server lights come on and a red beacon blinks on the roof.
// Construction accelerates until the plain is covered to the horizon.

type Hall = { x: number; z: number; w: number; d: number; h: number; build: number; seed: number };
export type Campus = { x: number; z: number; radius: number; build: number; seed: number };

/** Each campus's centre and size, for its glow of light pollution. */
export const CAMPUSES: Campus[] = [];

const NEAR_CAMPUSES = 230;
const FAR_CAMPUSES = 320;

const campus = (c: number, near: boolean, out: Hall[]) => {
  const r = (n: number) => hash(c, n, near ? 4242 : 5151);
  const side = r(1) < 0.5 ? -1 : 1;
  let sAlong: number;
  let dist: number;
  let build0: number;
  if (near) {
    // Beside the race, in view: each rises a few seconds before the pack arrives.
    sAlong = 10 + r(3) * 92;
    dist = (sAlong > 50 ? 16 : 7) + Math.pow(r(2), 1.5) * 18;
    build0 = Math.max(11.5, timeAtS(sAlong) - 2.5 - r(4) * 3);
  } else {
    // The boom: the whole plain fills, out to the horizon.
    sAlong = -20 + r(3) * 280;
    dist = 25 + Math.pow(r(2), 1.2) * 235;
    build0 = 12.5 + 6 * Math.sqrt(r(4)) + dist * 0.006;
  }
  const rows = 1 + Math.floor(r(5) * 3);
  const cols = near ? 2 + Math.floor(r(6) * 3) : 2 + Math.floor(r(6) * 4);
  const hw = near ? 3 + r(7) * 3 : 4 + r(7) * 5;
  const hd = 2 + r(8) * 1.6;
  const hh = near ? 0.7 + r(9) * 0.6 : 1.0 + r(9) * 1.2;
  // The campus grows away from the race, so its inner edge stays at dist.
  const extent = ((cols - 1) * (hw + 1.0)) / 2 + hw / 2;
  CAMPUSES.push({
    x: side * (dist + extent),
    z: -sAlong,
    radius: Math.max(extent, (rows * (hd + 1.4)) / 2),
    build: build0 + (rows * cols) * 0.04 + 0.9,
    seed: r(11),
  });
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const k = i * cols + j;
      out.push({
        x: side * (dist + extent) + (j - (cols - 1) / 2) * (hw + 1.0),
        z: -sAlong + (i - (rows - 1) / 2) * (hd + 1.4),
        w: hw,
        d: hd,
        h: hh * (0.85 + hash(c, k, 7) * 0.3),
        build: build0 + k * 0.08 + hash(c, k, 9) * 0.2,
        seed: hash(c, k, near ? 11 : 12),
      });
    }
  }
};

const halls: Hall[] = (() => {
  const out: Hall[] = [];
  for (let c = 0; c < NEAR_CAMPUSES; c++) campus(c, true, out);
  for (let c = 0; c < FAR_CAMPUSES; c++) campus(c, false, out);
  return out;
})();

export const HALL_COUNT = halls.length;

const vertexShader = /* glsl */ `
uniform float uTime;
attribute vec3 iSize;
attribute vec2 iBuild; // build start, seed
varying vec3 vLocal;
varying vec3 vNormalL;
varying vec3 vSize;
varying float vProgress;
varying float vSeed;
varying vec3 vWorld;
void main() {
  float p = clamp((uTime - iBuild.x) / 1.1, 0.0, 1.0);
  vProgress = p;
  vSeed = iBuild.y;
  vLocal = position;
  vNormalL = normal;
  vSize = iSize;
  vec3 pos = position;
  // The frame rises first.
  float rise = smoothstep(0.0, 0.45, p);
  pos.y = (pos.y + 0.5) * rise;
  vec4 wp = modelMatrix * instanceMatrix * vec4(pos, 1.0);
  vWorld = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
uniform float uTime;
uniform vec3 uBody;
uniform vec3 uEdge;
uniform vec3 uLed;
uniform vec3 uBeacon;
uniform vec3 uCam;
uniform float uFogDist;
uniform vec3 uFog;
varying vec3 vLocal;
varying vec3 vNormalL;
varying vec3 vSize;
varying float vProgress;
varying float vSeed;
varying vec3 vWorld;

float hash12(vec2 p) {
  vec3 p3 = fract(vec3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}

void main() {
  if (vProgress <= 0.0) discard;
  vec3 n = normalize(vNormalL);
  // Face-local coordinates in world units.
  vec2 uv;
  vec2 dim;
  bool top = n.y > 0.5;
  if (top) { uv = (vLocal.xz + 0.5) * vSize.xz; dim = vSize.xz; }
  else if (abs(n.x) > 0.5) { uv = vec2(vLocal.z + 0.5, vLocal.y + 0.5) * vec2(vSize.z, vSize.y); dim = vSize.zy; }
  else { uv = vec2(vLocal.x + 0.5, vLocal.y + 0.5) * vec2(vSize.x, vSize.y); dim = vSize.xy; }

  // Distance to the face's edges, in pixels, for crisp outlines at any distance.
  vec2 edgeDist = min(uv, dim - uv);
  vec2 fw = fwidth(uv);
  vec2 epx = edgeDist / max(fw, vec2(1e-5));
  float edge = 1.0 - smoothstep(0.6, 1.8, min(epx.x, epx.y));

  float frame = smoothstep(0.0, 0.08, vProgress);
  float shell = smoothstep(0.35, 0.65, vProgress);
  float lights = smoothstep(0.6, 1.0, vProgress);

  vec3 col = uBody * shell;
  // Construction glow on the edges fades to a quiet outline once built.
  float online = smoothstep(0.62, 0.7, vProgress) * (1.0 - smoothstep(0.7, 1.0, vProgress));
  float edgeGlow = (mix(2.8, 0.9, shell) + online * 3.0) * frame;
  // Far away the outline becomes a soft glow instead of vanishing.
  float far = smoothstep(0.02, 0.2, max(fw.x, fw.y));
  col += uEdge * mix(edge * edgeGlow, 0.18 * frame, far);

  if (!top) {
    // Rows of server lights: dashed horizontal strips that switch on bottom to top.
    float rowH = 0.22;
    float row = floor(uv.y / rowH);
    float inRow = fract(uv.y / rowH);
    float strip = smoothstep(0.42, 0.5, inRow) * (1.0 - smoothstep(0.58, 0.66, inRow));
    float cell = floor(uv.x / 0.18);
    float on = step(0.35, hash12(vec2(cell, row) + vSeed * 91.0));
    float flicker = 0.75 + 0.25 * sin(uTime * (3.0 + 7.0 * hash12(vec2(row, cell))) + vSeed * 40.0);
    float reach = step(uv.y / max(dim.y, 1e-3), lights * 1.05);
    float band = step(0.12, uv.y) * step(uv.y, dim.y - 0.12);
    // Strips resolve up close; far away they average into a glow, like city lights.
    float blur = smoothstep(0.06, 0.25, fwidth(uv.y) / rowH);
    float detail = strip * on * flicker * 3.2;
    col += uLed * mix(detail, 0.9, blur) * reach * band * (1.0 + online * 2.0);
  } else {
    // Cooling fans on the roof.
    vec2 g = fract(uv / 0.55) - 0.5;
    float fan = smoothstep(0.24, 0.2, length(g)) - smoothstep(0.16, 0.12, length(g));
    col += uEdge * fan * 0.25 * lights + uLed * 0.05 * lights;
    // Beacon at one corner.
    vec2 bc = vec2(0.25, 0.25);
    float b = smoothstep(0.12, 0.0, length(uv - bc));
    float blink = step(0.5, fract(uTime * 0.9 + vSeed * 3.0));
    col += uBeacon * b * blink * lights * 3.0;
  }

  float dist = length(vWorld - uCam);
  float fog = 1.0 - exp(-dist / uFogDist);
  col = mix(col, uFog, clamp(fog, 0.0, 1.0));
  gl_FragColor = vec4(col, 1.0);
}
`;

type Props = { t: number; cam: Vector3; fogDist: number; mapping: Mapping };

export const DataCenters: React.FC<Props> = ({ t, cam, fogDist, mapping }) => {
  const { sx, sy, sl } = mapping;
  const mesh = useMemo(() => {
    const geometry = new BoxGeometry(1, 1, 1);
    const size = new InstancedBufferAttribute(new Float32Array(HALL_COUNT * 3), 3);
    const build = new InstancedBufferAttribute(new Float32Array(HALL_COUNT * 2), 2);
    halls.forEach((h, i) => {
      size.setXYZ(i, h.w, h.h, h.d);
      build.setXY(i, h.build, h.seed);
    });
    geometry.setAttribute("iSize", size);
    geometry.setAttribute("iBuild", build);
    const material = new ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uBody: { value: new Color(PALETTE.datacenter) },
        uEdge: { value: new Color(PALETTE.led) },
        uLed: { value: new Color(PALETTE.led) },
        uBeacon: { value: new Color(PALETTE.beacon) },
        uCam: { value: new Vector3() },
        uFogDist: { value: 80 },
        uFog: { value: new Color(PALETTE.horizon) },
      },
    });
    const m = new InstancedMesh(geometry, material, HALL_COUNT);
    m.frustumCulled = false;
    return m;
  }, []);

  useLayoutEffect(() => {
    const mat = mesh.material as ShaderMaterial;
    mat.uniforms.uTime.value = t;
    mat.uniforms.uCam.value.copy(cam);
    mat.uniforms.uFogDist.value = fogDist;
    const m4 = new Matrix4();
    halls.forEach((h, i) => {
      m4.makeScale(h.w * sl, h.h * Math.min(1, sy), h.d * sx);
      m4.setPosition(h.x * sl, 0, h.z * sx);
      mesh.setMatrixAt(i, m4);
    });
    mesh.instanceMatrix.needsUpdate = true;
  });

  return <primitive object={mesh} />;
};
