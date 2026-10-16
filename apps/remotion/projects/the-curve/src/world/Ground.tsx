import { useLayoutEffect, useMemo } from "react";
import { Color, DoubleSide, ShaderMaterial, Vector3 } from "three";
import { CURVE_A, CURVE_L } from "../race";
import { PALETTE } from "../palette";
import { skyColorGlsl, skyUniforms } from "./skyColor";

// An endless chart floor: a fine dot grid with faint major lines, a soft light pool where the race
// runs along the ground, and fog that becomes exactly the sky colour at the horizon.

const vertexShader = /* glsl */ `
varying vec3 vWorld;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0);
  vWorld = wp.xyz;
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
${skyColorGlsl}
uniform vec3 uCam;
uniform vec3 uDot;
uniform vec3 uLine;
uniform vec3 uBase;
uniform vec3 uPool;
uniform float uFogDist;
uniform float uScale;
uniform float uHeadS;
uniform float uPoolWidth;
uniform float uPoolStrength;
uniform float uGrid;
uniform float uSx;
uniform float uSy;
varying vec3 vWorld;

float dots(vec2 p, float spacing, float radiusPx) {
  vec2 c = p / spacing;
  vec2 w = fwidth(c);
  vec2 f = abs(fract(c) - 0.5);
  vec2 px = f / max(w, vec2(1e-6));
  float r = length(px);
  float d = 1.0 - smoothstep(radiusPx, radiusPx + 1.0, r);
  float crowd = max(w.x, w.y);
  return d * (1.0 - smoothstep(0.05, 0.16, crowd));
}

float lines(vec2 p, float spacing, float widthPx) {
  vec2 c = p / spacing;
  vec2 w = fwidth(c);
  vec2 g = abs(fract(c) - 0.5) / max(w, vec2(1e-6));
  float line = 1.0 - smoothstep(widthPx * 0.5, widthPx * 0.5 + 1.0, min(g.x, g.y));
  float crowd = max(w.x, w.y);
  return line * (1.0 - smoothstep(0.04, 0.2, crowd));
}

void main() {
  vec2 p = vWorld.xz;
  vec3 toFrag = vWorld - uCam;
  float dist = length(toFrag);
  // Dots and lines fall on half cells, so nothing in the grid runs under the race at x = 0.
  float small = dots(p, uScale, 0.9);
  float big = dots(p, uScale * 10.0, 1.6);
  float majors = lines(p, uScale * 10.0, 0.7);
  vec3 col = uBase + (uDot * (small * 0.55 + big * 1.1) + uLine * majors * 0.6) * uGrid;

  // Light pool where the race lies flat along the ground, strongest under the sparks.
  float s = -vWorld.z / uSx;
  float h = ${CURVE_A.toFixed(4)} * (exp(min(s / ${CURVE_L.toFixed(1)}, 80.0)) - 1.0) * uSy;
  float along = smoothstep(-0.5, 0.5, s) * (1.0 - smoothstep(uHeadS - 0.5, uHeadS + 1.5, s)) * smoothstep(0.0, 2.0, uHeadS);
  float near = 0.25 + 0.75 * exp(-max(uHeadS - s, 0.0) / 6.0);
  float lift = exp(-h * 1.2);
  float pool = exp(-abs(vWorld.x) / uPoolWidth) * along * near * lift;
  col += uPool * pool * uPoolStrength;

  vec3 dir = normalize(vec3(toFrag.x, 0.0, toFrag.z));
  float fog = 1.0 - exp(-dist / uFogDist);
  col = mix(col, skyColor(dir), clamp(fog, 0.0, 1.0));
  gl_FragColor = vec4(col, 1.0);
}
`;

type Props = {
  cam: Vector3;
  headS: number;
  fogDist: number;
  scale?: number;
  grid?: number;
  poolStrength?: number;
  poolWidth?: number;
  sx?: number;
  sy?: number;
  dawn?: number;
};

export const Ground: React.FC<Props> = ({
  cam,
  headS,
  fogDist,
  scale = 1,
  grid = 1,
  poolStrength = 0.32,
  poolWidth = 0.9,
  sx = 1,
  sy = 1,
  dawn = 1,
}) => {
  const material = useMemo(
    () =>
      new ShaderMaterial({
        vertexShader,
        fragmentShader,
        side: DoubleSide,
        depthWrite: false,
        uniforms: {
          ...skyUniforms(),
          uCam: { value: new Vector3() },
          uDot: { value: new Color(PALETTE.gridDot) },
          uLine: { value: new Color(PALETTE.gridLine) },
          uBase: { value: new Color(PALETTE.ground) },
          uPool: { value: new Color(PALETTE.pool) },
          uFogDist: { value: 120 },
          uScale: { value: 1 },
          uHeadS: { value: 0 },
          uPoolWidth: { value: 1.6 },
          uPoolStrength: { value: 0.45 },
          uGrid: { value: 1 },
          uSx: { value: 1 },
          uSy: { value: 1 },
        },
      }),
    [],
  );
  useLayoutEffect(() => {
    const u = material.uniforms;
    u.uCam.value.copy(cam);
    u.uHeadS.value = headS;
    u.uFogDist.value = fogDist;
    u.uScale.value = scale;
    u.uGrid.value = grid;
    u.uPoolStrength.value = poolStrength;
    u.uPoolWidth.value = poolWidth;
    u.uSx.value = sx;
    u.uSy.value = sy;
    u.uDawnStrength.value = dawn;
  });
  return (
    <mesh material={material} rotation={[-Math.PI / 2, 0, 0]} renderOrder={-5} frustumCulled={false}>
      <planeGeometry args={[200000, 200000, 1, 1]} />
    </mesh>
  );
};
