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

const finish = (parts: BufferGeometry[]) => {
  const nonIndexed = parts.map((p) => (p.index ? p.toNonIndexed() : p));
  for (const p of nonIndexed) {
    p.deleteAttribute("uv");
  }
  // Each part keeps its own smooth normals; recomputing them on the merged soup would facet the rim.
  return mergeGeometries(nonIndexed, false);
};

/** Everything below the neck: coat, arms, hands, legs and shoes. Faces −Z. */
export const buildBody = () => {
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
  return finish([
    coat,
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
  ]);
};

/** NECK is the head's pivot; the head geometry is built around it. Nose and ears show which way it turns. */
export const NECK = 1.49;
export const buildHead = () =>
  finish([
    place(new CylinderGeometry(0.044, 0.05, 0.13, 12), [0, 0.045, 0]),
    place(new SphereGeometry(0.098, 24, 16), [0, 0.165, 0.008], [0, 0, 0], [0.86, 1.04, 0.98]),
    // Hair: a little more volume at the back and crown
    place(new SphereGeometry(0.094, 20, 14), [0, 0.19, 0.022], [0, 0, 0], [0.9, 0.86, 0.94]),
    // Nose and ears
    place(new CapsuleGeometry(0.016, 0.03, 4, 8), [0, 0.152, -0.088], [0.25, 0, 0]),
    place(new SphereGeometry(0.022, 10, 8), [-0.084, 0.158, 0.01], [0, 0, 0], [0.55, 1, 0.8]),
    place(new SphereGeometry(0.022, 10, 8), [0.084, 0.158, 0.01], [0, 0, 0], [0.55, 1, 0.8]),
  ]);

/** The crowd's single merged figure, head tipped back by lookUp (0–1). */
export const buildFigure = (lookUp = 0) => {
  const head = buildHead();
  head.applyMatrix4(
    new Matrix4().compose(
      new Vector3(0, NECK, 0),
      new Quaternion().setFromEuler(new Euler(0.55 * lookUp, 0, 0)),
      new Vector3(1, 1, 1),
    ),
  );
  return finish([buildBody(), head]);
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
  float fres = pow(1.0 - clamp(abs(dot(N, V)), 0.0, 1.0), 4.0);
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

/** How the person stands: turned (yaw), head turned and tipped up, leaning back, stepped back. */
export type Pose = { yaw: number; headYaw: number; headPitch: number; lean: number; step: number; bob: number };
export const STILL: Pose = { yaw: 0, headYaw: 0, headPitch: 0, lean: 0, step: 0, bob: 0 };

type Props = {
  cam: Vector3;
  light: Vector3;
  position?: [number, number, number];
  pose?: Pose;
  rim?: number;
};

export const Figure: React.FC<Props> = ({ cam, light, position = [0, 0, 0], pose = STILL, rim = 1.6 }) => {
  const body = useMemo(buildBody, []);
  const head = useMemo(buildHead, []);
  const material = useMemo(createFigureMaterial, []);
  useLayoutEffect(() => {
    material.uniforms.uCam.value.copy(cam);
    material.uniforms.uLight.value.copy(light);
    material.uniforms.uRimStrength.value = rim;
  });
  // Stepping back moves against the way the person faces.
  const back: [number, number, number] = [
    position[0] + Math.sin(pose.yaw) * pose.step,
    position[1] + pose.bob,
    position[2] + Math.cos(pose.yaw) * pose.step,
  ];
  return (
    <group position={back} rotation={[0, pose.yaw, 0]}>
      <group rotation={[pose.lean, 0, 0]}>
        <mesh geometry={body} material={material} />
        <group position={[0, NECK, 0]} rotation={[0, pose.headYaw, 0]}>
          <group rotation={[pose.headPitch, 0, 0]}>
            <mesh geometry={head} material={material} />
          </group>
        </group>
      </group>
    </group>
  );
};
