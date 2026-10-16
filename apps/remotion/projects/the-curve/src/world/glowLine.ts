import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  Color,
  DoubleSide,
  ShaderMaterial,
  Vector2,
  Vector3,
} from "three";

// A line drawn as a camera-facing strip: a white-hot core inside a coloured halo. Its width is
// whichever is larger of a pixel minimum and a world width, so it stays visible from any distance
// and becomes a tube of light up close. Vertices behind the near plane are pulled onto it.

const vertexShader = /* glsl */ `
uniform vec2 uResolution;
uniform float uMinPx;
uniform float uMaxPx;
uniform float uWorldWidth;
uniform float uNear;
attribute vec3 aPrev;
attribute vec3 aNext;
attribute float aSide;
attribute float aB;
attribute vec3 aColor;
varying float vSide;
varying float vB;
varying vec3 vColor;
varying float vPx;

void main() {
  vec4 vc = modelViewMatrix * vec4(position, 1.0);
  vec4 vp = modelViewMatrix * vec4(aPrev, 1.0);
  vec4 vn = modelViewMatrix * vec4(aNext, 1.0);
  float nz = -uNear * 1.01;
  if (vc.z > nz) {
    if (vn.z < nz) vc = mix(vc, vn, (nz - vc.z) / (vn.z - vc.z));
    else if (vp.z < nz) vc = mix(vc, vp, (nz - vc.z) / (vp.z - vc.z));
    else { gl_Position = vec4(0.0, 0.0, 2.0, 1.0); vB = 0.0; vSide = 0.0; vColor = vec3(0.0); vPx = 1.0; return; }
  }
  if (vp.z > nz) vp = vc - (vn - vc);
  if (vn.z > nz) vn = vc + (vc - vp);

  vec4 cc = projectionMatrix * vc;
  vec4 cp = projectionMatrix * vp;
  vec4 cn = projectionMatrix * vn;
  float aspect = uResolution.x / uResolution.y;
  vec2 sc = cc.xy / cc.w; sc.x *= aspect;
  vec2 sp = cp.xy / cp.w; sp.x *= aspect;
  vec2 sn = cn.xy / cn.w; sn.x *= aspect;
  vec2 d0 = sc - sp;
  vec2 d1 = sn - sc;
  float l0 = length(d0);
  float l1 = length(d1);
  vec2 dir = vec2(1.0, 0.0);
  if (l0 > 1e-7 && l1 > 1e-7) dir = normalize(d0 / l0 + d1 / l1 + 1e-9);
  else if (l1 > 1e-7) dir = d1 / l1;
  else if (l0 > 1e-7) dir = d0 / l0;
  vec2 nrm = vec2(-dir.y, dir.x);

  float pxPerUnit = projectionMatrix[1][1] * 0.5 * uResolution.y / max(-vc.z, 1e-4);
  float px = clamp(uWorldWidth * pxPerUnit, uMinPx, uMaxPx);
  vec2 offset = nrm * (px * aSide) / uResolution.y; // half width each side, in NDC y units
  offset.x /= aspect;
  cc.xy += offset * cc.w;
  gl_Position = cc;
  vSide = aSide;
  vB = aB;
  vColor = aColor;
  vPx = px;
}
`;

const fragmentShader = /* glsl */ `
uniform float uIntensity;
uniform float uCoreFrac;
varying float vSide;
varying float vB;
varying vec3 vColor;
varying float vPx;

void main() {
  float d = abs(vSide);
  // Keep the core at least ~1.6 px wide however thin the strip is.
  float coreHalf = max(uCoreFrac, 0.8 / max(vPx * 0.5, 1.0));
  float core = 1.0 - smoothstep(coreHalf * 0.45, coreHalf, d);
  float halo = exp(-d * d * 5.0) - exp(-5.0);
  vec3 white = mix(vColor, vec3(1.0), 0.75);
  vec3 col = white * core * 2.2 + vColor * max(halo, 0.0) * 0.55;
  gl_FragColor = vec4(col * vB * uIntensity, 1.0);
}
`;

export const createGlowLineMaterial = () =>
  new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uResolution: { value: new Vector2(1920, 1080) },
      uMinPx: { value: 9 },
      uMaxPx: { value: 260 },
      uWorldWidth: { value: 0.12 },
      uNear: { value: 0.05 },
      uIntensity: { value: 1 },
      uCoreFrac: { value: 0.16 },
    },
    transparent: true,
    depthWrite: false,
    depthTest: true,
    // Strip winding flips with the line's screen direction.
    side: DoubleSide,
    blending: AdditiveBlending,
  });

/** Accumulates polylines into one strip geometry, rebuilt every frame. */
export class LineBatch {
  readonly geometry = new BufferGeometry();
  private capacity = 0;
  private points = 0;
  private indexCount = 0;
  private pos!: Float32Array;
  private prev!: Float32Array;
  private next!: Float32Array;
  private side!: Float32Array;
  private bright!: Float32Array;
  private color!: Float32Array;
  private index!: Uint32Array;

  constructor(capacity = 8192) {
    this.allocate(capacity);
  }

  private allocate(capacity: number) {
    this.capacity = capacity;
    const v = capacity * 2;
    this.pos = new Float32Array(v * 3);
    this.prev = new Float32Array(v * 3);
    this.next = new Float32Array(v * 3);
    this.side = new Float32Array(v);
    this.bright = new Float32Array(v);
    this.color = new Float32Array(v * 3);
    this.index = new Uint32Array(capacity * 6);
    for (let i = 0; i < capacity; i++) {
      this.side[i * 2] = -1;
      this.side[i * 2 + 1] = 1;
    }
    this.geometry.setAttribute("position", new BufferAttribute(this.pos, 3));
    this.geometry.setAttribute("aPrev", new BufferAttribute(this.prev, 3));
    this.geometry.setAttribute("aNext", new BufferAttribute(this.next, 3));
    this.geometry.setAttribute("aSide", new BufferAttribute(this.side, 1));
    this.geometry.setAttribute("aB", new BufferAttribute(this.bright, 1));
    this.geometry.setAttribute("aColor", new BufferAttribute(this.color, 3));
    this.geometry.setIndex(new BufferAttribute(this.index, 1));
  }

  begin() {
    this.points = 0;
    this.indexCount = 0;
  }

  /** Adds one polyline. brightness has one value per point; colors, if given, too. */
  add(pts: Vector3[], brightness: number[], color: Color, colors?: Color[]) {
    const n = pts.length;
    if (n < 2) return;
    if (this.points + n > this.capacity) {
      const keepPoints = this.points;
      const keepIndex = this.indexCount;
      const old = { pos: this.pos, prev: this.prev, next: this.next, bright: this.bright, color: this.color, index: this.index };
      this.allocate(Math.max(this.capacity * 2, this.points + n));
      this.pos.set(old.pos.subarray(0, keepPoints * 6));
      this.prev.set(old.prev.subarray(0, keepPoints * 6));
      this.next.set(old.next.subarray(0, keepPoints * 6));
      this.bright.set(old.bright.subarray(0, keepPoints * 2));
      this.color.set(old.color.subarray(0, keepPoints * 6));
      this.index.set(old.index.subarray(0, keepIndex));
    }
    const base = this.points;
    for (let i = 0; i < n; i++) {
      const p = pts[i];
      const a = pts[Math.max(0, i - 1)];
      const b = pts[Math.min(n - 1, i + 1)];
      for (let k = 0; k < 2; k++) {
        const v = (base + i) * 2 + k;
        this.pos[v * 3] = p.x;
        this.pos[v * 3 + 1] = p.y;
        this.pos[v * 3 + 2] = p.z;
        this.prev[v * 3] = a.x;
        this.prev[v * 3 + 1] = a.y;
        this.prev[v * 3 + 2] = a.z;
        this.next[v * 3] = b.x;
        this.next[v * 3 + 1] = b.y;
        this.next[v * 3 + 2] = b.z;
        this.bright[v] = brightness[i];
        const c = colors ? colors[i] : color;
        this.color[v * 3] = c.r;
        this.color[v * 3 + 1] = c.g;
        this.color[v * 3 + 2] = c.b;
      }
      if (i < n - 1) {
        const v0 = (base + i) * 2;
        const ii = this.indexCount;
        this.index[ii] = v0;
        this.index[ii + 1] = v0 + 1;
        this.index[ii + 2] = v0 + 2;
        this.index[ii + 3] = v0 + 2;
        this.index[ii + 4] = v0 + 1;
        this.index[ii + 5] = v0 + 3;
        this.indexCount += 6;
      }
    }
    this.points += n;
  }

  end() {
    const g = this.geometry;
    for (const name of ["position", "aPrev", "aNext", "aSide", "aB", "aColor"]) {
      const attr = g.getAttribute(name) as BufferAttribute;
      attr.needsUpdate = true;
    }
    (g.getIndex() as BufferAttribute).needsUpdate = true;
    g.setDrawRange(0, this.indexCount);
    // The strip is expanded in the vertex shader; skip culling instead of guessing bounds.
    g.boundingSphere = null;
  }
}

export const tmpVec = () => new Vector3();
