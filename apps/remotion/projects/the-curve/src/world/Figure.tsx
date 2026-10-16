import { useLayoutEffect, useMemo } from "react";
import {
  BufferGeometry,
  CapsuleGeometry,
  Color,
  CylinderGeometry,
  Euler,
  LatheGeometry,
  Matrix4,
  Quaternion,
  ShaderMaterial,
  SphereGeometry,
  Vector2,
  Vector3,
} from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { PALETTE } from "../palette";

// A person in a long coat, seen from behind: black, with a thin rim of the light ahead of them.

const place = (g: BufferGeometry, pos: [number, number, number], rot: [number, number, number] = [0, 0, 0], scale: [number, number, number] = [1, 1, 1]) => {
  const m = new Matrix4().compose(
    new Vector3(...pos),
    new Quaternion().setFromEuler(new Euler(...rot)),
    new Vector3(...scale),
  );
  g.applyMatrix4(m);
  return g;
};

/** lookUp tilts the head back (0 = level, 1 = looking high up). */
export const buildFigure = (lookUp = 0) => {
  // Coat as a lathe: sloping shoulders, a slight waist, a flare to the knees; flattened front to back.
  const profile = [
    [0.0, 1.5],
    [0.1, 1.495],
    [0.175, 1.47],
    [0.205, 1.42],
    [0.2, 1.3],
    [0.185, 1.12],
    [0.19, 0.98],
    [0.215, 0.8],
    [0.245, 0.6],
    [0.25, 0.56],
  ].map(([r, y]) => new Vector2(r, y));
  const coat = new LatheGeometry(profile, 28);
  coat.scale(1, 1, 0.62);
  const tilt = 0.45 * lookUp;
  const parts = [
    coat,
    // Head and neck; looking up shifts the head back and tips it.
    place(new SphereGeometry(0.098, 24, 16), [0, 1.655 - 0.02 * lookUp, 0.035 * lookUp], [tilt, 0, 0], [0.86, 1.04, 0.96]),
    place(new CylinderGeometry(0.044, 0.05, 0.12, 12), [0, 1.535, 0.012 * lookUp], [tilt * 0.5, 0, 0]),
    // Arms hanging just outside the coat
    place(new CapsuleGeometry(0.048, 0.52, 6, 12), [-0.215, 1.15, 0.005], [0, 0, -0.06]),
    place(new CapsuleGeometry(0.048, 0.52, 6, 12), [0.215, 1.15, 0.005], [0, 0, 0.06]),
    // Hands
    place(new SphereGeometry(0.042, 10, 8), [-0.232, 0.86, 0.01]),
    place(new SphereGeometry(0.042, 10, 8), [0.232, 0.86, 0.01]),
    // Legs and shoes
    place(new CapsuleGeometry(0.058, 0.5, 6, 10), [-0.085, 0.33, 0], [0, 0, 0.015]),
    place(new CapsuleGeometry(0.058, 0.5, 6, 10), [0.085, 0.33, 0], [0, 0, -0.015]),
    place(new CapsuleGeometry(0.045, 0.13, 4, 8), [-0.088, 0.045, -0.045], [Math.PI / 2, 0, 0], [1, 1, 0.8]),
    place(new CapsuleGeometry(0.045, 0.13, 4, 8), [0.088, 0.045, -0.045], [Math.PI / 2, 0, 0], [1, 1, 0.8]),
  ];
  const nonIndexed = parts.map((p) => (p.index ? p.toNonIndexed() : p));
  for (const p of nonIndexed) {
    p.deleteAttribute("uv");
  }
  // Each part keeps its own smooth normals; recomputing them on the merged soup would facet the rim.
  return mergeGeometries(nonIndexed, false);
};

const vertexShader = /* glsl */ `
varying vec3 vN;
varying vec3 vWorld;
void main() {
#ifdef USE_INSTANCING
  mat4 m = modelMatrix * instanceMatrix;
#else
  mat4 m = modelMatrix;
#endif
  vec4 wp = m * vec4(position, 1.0);
  vWorld = wp.xyz;
  vN = normalize(mat3(m) * normal);
  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const fragmentShader = /* glsl */ `
uniform vec3 uCam;
uniform vec3 uLight;
uniform vec3 uRim;
uniform float uRimStrength;
varying vec3 vN;
varying vec3 vWorld;
void main() {
  vec3 N = normalize(vN);
  vec3 V = normalize(uCam - vWorld);
  vec3 L = normalize(uLight - vWorld);
  float fres = pow(1.0 - clamp(abs(dot(N, V)), 0.0, 1.0), 2.5);
  float facing = smoothstep(-0.2, 0.8, dot(N, L));
  vec3 col = uRim * fres * facing * uRimStrength;
  gl_FragColor = vec4(col, 1.0);
}
`;

export const createFigureMaterial = () =>
  new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uCam: { value: new Vector3() },
      uLight: { value: new Vector3(0, 2, -30) },
      uRim: { value: new Color(PALETTE.rim) },
      uRimStrength: { value: 1.2 },
    },
  });

type Props = {
  cam: Vector3;
  light: Vector3;
  position?: [number, number, number];
  rotationY?: number;
  lookUp?: number;
  rim?: number;
};

export const Figure: React.FC<Props> = ({ cam, light, position = [0, 0, 0], rotationY = 0, lookUp = 0, rim = 1.6 }) => {
  const geometry = useMemo(() => buildFigure(lookUp), [lookUp]);
  const material = useMemo(createFigureMaterial, []);
  useLayoutEffect(() => {
    material.uniforms.uCam.value.copy(cam);
    material.uniforms.uLight.value.copy(light);
    material.uniforms.uRimStrength.value = rim;
  });
  return <mesh geometry={geometry} material={material} position={position} rotation={[0, rotationY, 0]} />;
};
