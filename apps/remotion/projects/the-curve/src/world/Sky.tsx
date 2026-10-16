import { useLayoutEffect, useMemo } from "react";
import { BackSide, ShaderMaterial, Vector3 } from "three";
import { skyColorGlsl, skyUniforms } from "./skyColor";

// A dome that travels with the camera: night gradient, a haze band and dawn on the horizon ahead,
// and sparse fixed stars.

const vertexShader = /* glsl */ `
varying vec3 vDir;
void main() {
  vDir = normalize(position);
  vec4 wp = modelMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
${skyColorGlsl}
uniform float uStars;
varying vec3 vDir;

float hash21(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

void main() {
  vec3 d = normalize(vDir);
  vec3 col = skyColor(d);
  vec2 uv = vec2(atan(d.x, -d.z), asin(clamp(d.y, -1.0, 1.0))) * 260.0;
  vec2 cell = floor(uv);
  float h = hash21(cell);
  vec2 offs = vec2(hash21(cell + 7.1), hash21(cell + 3.3)) - 0.5;
  float r = length(fract(uv) - 0.5 - offs * 0.6);
  float star = step(0.993, h) * smoothstep(0.2, 0.0, r) * (0.25 + 0.75 * pow(hash21(cell + 1.7), 3.0));
  col += vec3(0.78, 0.84, 1.0) * star * smoothstep(0.06, 0.35, d.y) * uStars;
  gl_FragColor = vec4(col, 1.0);
}
`;

type Props = { cam: Vector3; glow?: number; dawn?: number; stars?: number; radius?: number };

export const Sky: React.FC<Props> = ({ cam, glow = 1, dawn = 1, stars = 1, radius = 9000 }) => {
  const material = useMemo(
    () =>
      new ShaderMaterial({
        vertexShader,
        fragmentShader,
        side: BackSide,
        depthWrite: false,
        depthTest: false,
        uniforms: { ...skyUniforms(), uStars: { value: 1 } },
      }),
    [],
  );
  useLayoutEffect(() => {
    const u = material.uniforms;
    u.uGlowStrength.value = glow;
    u.uDawnStrength.value = dawn;
    u.uStars.value = stars;
  });
  return (
    <mesh material={material} position={cam} scale={radius} renderOrder={-10} frustumCulled={false}>
      <sphereGeometry args={[1, 64, 32]} />
    </mesh>
  );
};
