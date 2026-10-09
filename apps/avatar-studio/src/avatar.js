import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const clamp = (value, min = 0, max = 1) => THREE.MathUtils.clamp(Number(value) || 0, min, max);
const V = (x, y, z) => new THREE.Vector3(x, y, z);

/** A completely local, procedural character. Time is supplied by the caller. */
export function createAvatar(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(globalThis.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e9e4dc');
  scene.fog = new THREE.Fog('#e9e4dc', 10, 23);
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 50);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.enablePan = false;
  controls.minDistance = 3.1;
  controls.maxDistance = 8.5;
  controls.minPolarAngle = 0.65;
  controls.maxPolarAngle = 1.84;
  controls.rotateSpeed = 0.65;

  const material = (color, roughness = 0.72, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness, ...extra });
  const skin = material('#c99172', 0.64);
  const skinDetail = material('#ae735b', 0.8);
  const lips = material('#9f5c51', 0.71);
  const hair = material('#3a2925', 0.66);
  const hairHighlight = material('#47322c', 0.72);
  const shirt = material('#52756e', 0.94);
  const shirtTrim = material('#42655e', 0.92);
  const sclera = material('#fff9ed', 0.32);
  const iris = material('#647e75', 0.4);
  const pupil = material('#192321', 0.3);
  const mouthMaterial = material('#532b2b', 0.98);
  const teethMaterial = material('#f2e2cc', 0.55);
  const frameMaterial = material('#3b302b', 0.37, { metalness: 0.18 });

  const sphereGeometry = new THREE.SphereGeometry(1, 48, 32);
  function ellipsoid(parent, mat, position, scale, geometry = sphereGeometry) {
    const mesh = new THREE.Mesh(geometry, mat);
    mesh.position.set(...position);
    mesh.scale.set(...scale);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  }

  function tube(parent, points, radius, mat, closed = false, segments = 32) {
    const curve = new THREE.CatmullRomCurve3(points.map((point) => Array.isArray(point) ? V(...point) : point), closed);
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 8, closed), mat);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  }

  scene.add(new THREE.HemisphereLight('#fffbef', '#a5a29a', 2.7));
  const key = new THREE.DirectionalLight('#fff0da', 3.8);
  key.position.set(-3.8, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -3.5;
  key.shadow.camera.right = 3.5;
  key.shadow.camera.top = 5;
  key.shadow.camera.bottom = -2;
  key.shadow.normalBias = 0.022;
  key.shadow.bias = -0.0001;
  key.shadow.radius = 4;
  key.target.position.set(0, 1.8, 0);
  scene.add(key, key.target);
  const fill = new THREE.DirectionalLight('#d5e9ee', 1.35);
  fill.position.set(4, 3.5, 2.5);
  scene.add(fill);
  const rim = new THREE.DirectionalLight('#fff3d7', 2.2);
  rim.position.set(1, 5, -3.5);
  scene.add(rim);

  const floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), material('#e4dfd6', 1));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.035;
  floor.receiveShadow = true;
  scene.add(floor);
  const plinth = new THREE.Mesh(new THREE.CylinderGeometry(1.38, 1.42, 0.075, 96), material('#d8d1c6', 0.95));
  plinth.position.y = 0.005;
  plinth.receiveShadow = true;
  scene.add(plinth);

  const body = new THREE.Group();
  scene.add(body);
  const torsoPoints = [
    [0.0, 0.12], [0.50, 0.12], [0.60, 0.16], [0.65, 0.32], [0.68, 0.65],
    [0.73, 1.02], [0.78, 1.29], [0.75, 1.47], [0.62, 1.64], [0.39, 1.78], [0.22, 1.80], [0, 1.80],
  ].map(([x, y]) => new THREE.Vector2(x, y));
  const torso = new THREE.Mesh(new THREE.LatheGeometry(torsoPoints, 64), shirt);
  torso.scale.z = 0.61;
  torso.castShadow = true;
  torso.receiveShadow = true;
  body.add(torso);

  ellipsoid(body, skin, [0, 1.91, 0], [0.235, 0.41, 0.215]);
  // A rolled neckline and restrained garment seams keep the bust readable from all sides.
  for (let row = 0; row < 4; row++) {
    const collar = new THREE.Mesh(new THREE.TorusGeometry(0.265, 0.037, 10, 64), shirtTrim);
    collar.rotation.x = Math.PI / 2;
    collar.scale.y = 0.83;
    collar.position.set(0, 1.77 + row * 0.024, 0.018);
    collar.castShadow = true;
    body.add(collar);
  }
  tube(body, [[-0.38, 1.70, 0.15], [-0.51, 1.53, 0.28], [-0.63, 1.38, 0.30]], 0.009, shirtTrim);
  tube(body, [[0.38, 1.70, 0.15], [0.51, 1.53, 0.28], [0.63, 1.38, 0.30]], 0.009, shirtTrim);
  const hem = new THREE.Mesh(new THREE.TorusGeometry(0.59, 0.023, 8, 64), shirtTrim);
  hem.rotation.x = Math.PI / 2;
  hem.scale.y = 0.61;
  hem.position.y = 0.20;
  body.add(hem);

  const arms = [];
  for (const side of [-1, 1]) {
    const arm = new THREE.Group();
    arm.position.set(side * 0.65, 1.48, 0.005);
    arm.rotation.z = side * 0.11;
    body.add(arm);
    ellipsoid(arm, shirt, [side * 0.05, -0.31, 0], [0.25, 0.49, 0.255]);
    const forearm = new THREE.Group();
    forearm.position.set(side * 0.035, -0.65, 0.025);
    arm.add(forearm);
    ellipsoid(forearm, shirt, [0, -0.19, 0], [0.195, 0.32, 0.20]);
    const cuff = new THREE.Mesh(new THREE.CylinderGeometry(0.155, 0.158, 0.09, 40), shirtTrim);
    cuff.position.y = -0.44;
    cuff.castShadow = true;
    forearm.add(cuff);
    const hand = new THREE.Group();
    hand.position.set(0, -0.54, 0.025);
    forearm.add(hand);
    ellipsoid(hand, skin, [0, -0.04, 0], [0.128, 0.16, 0.082]);
    for (let finger = 0; finger < 4; finger++) {
      ellipsoid(hand, skin, [(finger - 1.5) * 0.057, -0.168 - Math.sin(finger * 0.9) * 0.018, 0.006], [0.032, 0.094, 0.038]);
    }
    const thumb = ellipsoid(hand, skin, [-side * 0.122, -0.03, 0.016], [0.049, 0.093, 0.045]);
    thumb.rotation.z = -side * 0.35;
    arms.push({ arm, forearm, side });
  }

  const headPivot = new THREE.Group();
  headPivot.position.set(0, 2.08, 0);
  body.add(headPivot);
  const head = new THREE.Group();
  head.position.y = 0.53;
  headPivot.add(head);

  const headGeometry = new THREE.SphereGeometry(1, 80, 64);
  const positions = headGeometry.attributes.position;
  for (let index = 0; index < positions.count; index++) {
    const y = positions.getY(index);
    const jaw = y < -0.23 ? 1 - 0.16 * Math.min(1, (-y - 0.23) / 0.62) : 1;
    positions.setXYZ(index, positions.getX(index) * 0.565 * jaw, y * 0.76, positions.getZ(index) * 0.465 * (y < -0.50 ? 0.96 : 1));
  }
  headGeometry.computeVertexNormals();
  ellipsoid(head, skin, [0, 0, 0], [1, 1, 1], headGeometry);

  for (const side of [-1, 1]) {
    const ear = ellipsoid(head, skin, [side * 0.552, -0.025, -0.015], [0.115, 0.184, 0.108]);
    ear.rotation.z = -side * 0.10;
    ellipsoid(head, skinDetail, [side * 0.591, -0.019, 0.067], [0.050, 0.110, 0.025]);
    ellipsoid(head, skin, [side * 0.574, -0.048, 0.084], [0.035, 0.069, 0.029]);
  }

  ellipsoid(head, skin, [0, 0.005, 0.465], [0.069, 0.158, 0.085]);
  ellipsoid(head, skin, [0, -0.100, 0.520], [0.094, 0.080, 0.099]);
  for (const side of [-1, 1]) {
    ellipsoid(head, skin, [side * 0.076, -0.126, 0.488], [0.049, 0.045, 0.058]);
    const nostril = ellipsoid(head, skinDetail, [side * 0.055, -0.153, 0.538], [0.025, 0.012, 0.020]);
    nostril.rotation.z = side * 0.13;
  }

  const eyes = [];
  const eyebrows = [];
  for (const side of [-1, 1]) {
    const eye = new THREE.Group();
    eye.position.set(side * 0.221, 0.123, 0.421);
    head.add(eye);
    ellipsoid(eye, sclera, [0, 0, 0], [0.135, 0.085, 0.075]);
    const eyeColor = ellipsoid(eye, iris, [-side * 0.005, 0, 0.067], [0.046, 0.049, 0.012]);
    ellipsoid(eyeColor, pupil, [0, 0, 0.64], [0.51, 0.54, 0.50]);
    ellipsoid(eye, sclera, [-0.012 - side * 0.005, 0.017, 0.080], [0.012, 0.012, 0.005]);
    ellipsoid(eye, sclera, [0.013 - side * 0.005, -0.014, 0.079], [0.005, 0.005, 0.003]);
    const upper = [];
    const lower = [];
    for (let step = 0; step <= 16; step++) {
      const t = step / 16;
      const x = (t * 2 - 1) * 0.132;
      const z = 0.026 + Math.sin(t * Math.PI) * 0.030;
      upper.push([x, Math.sin(t * Math.PI) * 0.073, z]);
      lower.push([x, -Math.sin(t * Math.PI) * 0.064, z]);
    }
    tube(eye, upper, 0.016, skin);
    tube(eye, lower, 0.012, skin);
    eyes.push(eye);
    const browGroup = new THREE.Group();
    browGroup.position.set(side * 0.221, 0.276, 0.425);
    head.add(browGroup);
    tube(browGroup, [[-0.119, -0.013 * side, -0.018], [-0.055, 0.017, 0.012], [0.021, 0.027, 0.015], [0.112, -0.004 * side, -0.014]], 0.024, hair);
    eyebrows.push({ group: browGroup, side });
  }

  // The mouth is a curved surface conforming to the lower face. Only its vertices move.
  const mouthSegments = 40;
  const mouthGeometry = new THREE.BufferGeometry();
  const mouthVertices = new Float32Array((mouthSegments + 2) * 3);
  const mouthIndices = [];
  for (let index = 0; index < mouthSegments; index++) mouthIndices.push(0, index + 1, (index + 1) % mouthSegments + 1);
  mouthGeometry.setAttribute('position', new THREE.BufferAttribute(mouthVertices, 3).setUsage(THREE.DynamicDrawUsage));
  mouthGeometry.setIndex(mouthIndices);
  const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
  mouth.material.side = THREE.DoubleSide;
  head.add(mouth);
  const upperLip = tube(head, [[-0.16, -0.30, 0.45], [0, -0.31, 0.46], [0.16, -0.30, 0.45]], 0.013, lips);
  const lowerLip = tube(head, [[-0.16, -0.30, 0.45], [0, -0.34, 0.46], [0.16, -0.30, 0.45]], 0.016, lips);
  // Deform the existing lip tubes without allocating fresh geometries each frame.
  const lipRestPositions = [upperLip, lowerLip].map((mesh) => Float32Array.from(mesh.geometry.attributes.position.array));
  const teeth = ellipsoid(head, teethMaterial, [0, -0.299, 0.459], [0.126, 0.023, 0.008]);
  const tongue = ellipsoid(head, lips, [0, -0.35, 0.447], [0.091, 0.02, 0.008]);

  const hairGroups = { swept: new THREE.Group(), crop: new THREE.Group(), bald: new THREE.Group() };
  Object.values(hairGroups).forEach((group) => head.add(group));
  function makeHairCap(parent, short) {
    const geometry = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];
    const radial = 64;
    const rings = 26;
    for (let ring = 0; ring <= rings; ring++) {
      for (let segment = 0; segment <= radial; segment++) {
        const phi = segment / radial * Math.PI * 2;
        const front = Math.cos(phi);
        const limit = 1.65 - Math.max(0, front) * 0.60 + Math.max(0, -front) * 0.28;
        const theta = ring / rings * limit;
        const radius = short ? 1.014 : 1.038;
        vertices.push(Math.sin(theta) * Math.sin(phi) * 0.565 * radius, Math.cos(theta) * 0.77 * radius, Math.sin(theta) * Math.cos(phi) * 0.474 * radius);
      }
    }
    for (let ring = 0; ring < rings; ring++) {
      for (let segment = 0; segment < radial; segment++) {
        const a = ring * (radial + 1) + segment;
        const b = a + radial + 1;
        indices.push(a, a + 1, b, b, a + 1, b + 1);
      }
    }
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    const cap = new THREE.Mesh(geometry, hair);
    cap.material.side = THREE.DoubleSide;
    cap.castShadow = true;
    cap.receiveShadow = true;
    parent.add(cap);
  }
  makeHairCap(hairGroups.swept, false);
  makeHairCap(hairGroups.crop, true);
  for (let strand = 0; strand < 8; strand++) {
    const p = strand / 7;
    const lock = tube(hairGroups.swept, [
      [-0.44 + p * 0.16, 0.45 + p * 0.10, 0.33 - p * 0.12],
      [-0.26 + p * 0.11, 0.72 + p * 0.045, 0.29 - p * 0.16],
      [0.05 + p * 0.16, 0.80 - p * 0.038, 0.16 - p * 0.21],
      [0.37 + p * 0.08, 0.56 - p * 0.025, -0.02 - p * 0.25],
    ], 0.054 - p * 0.015, strand % 3 === 1 ? hairHighlight : hair, false, 40);
    lock.scale.y = 1.015;
  }
  for (let strand = 0; strand < 14; strand++) {
    const phi = strand / 14 * Math.PI * 2;
    const points = [];
    for (let step = 0; step <= 16; step++) {
      const theta = 0.17 + step / 16 * (Math.cos(phi) > 0 ? 0.83 : 1.33);
      const angle = phi + Math.sin(theta) * 0.15;
      points.push([Math.sin(theta) * Math.sin(angle) * 0.580, Math.cos(theta) * 0.792, Math.sin(theta) * Math.cos(angle) * 0.487]);
    }
    tube(hairGroups.crop, points, 0.006, hairHighlight, false, 24);
  }

  const glasses = new THREE.Group();
  head.add(glasses);
  for (const side of [-1, 1]) {
    const points = [];
    for (let step = 0; step < 48; step++) {
      const angle = step / 48 * Math.PI * 2;
      points.push([side * 0.223 + Math.cos(angle) * 0.166, 0.126 + Math.sin(angle) * 0.123, 0.525 - Math.abs(Math.cos(angle)) * 0.021]);
    }
    tube(glasses, points, 0.013, frameMaterial, true, 64);
    tube(glasses, [[side * 0.385, 0.155, 0.510], [side * 0.495, 0.166, 0.30], [side * 0.566, 0.113, 0.00]], 0.011, frameMaterial);
  }
  tube(glasses, [[-0.058, 0.144, 0.528], [0, 0.165, 0.544], [0.058, 0.144, 0.528]], 0.012, frameMaterial);
  glasses.visible = false;

  let expression = 0.55;
  let gesture = 0.28;
  let speaking = false;
  let targetEnergy = 0;
  let energy = 0;
  let previousTime;
  let disposed = false;

  function updateAppearance(appearance = {}) {
    if (appearance.skin) {
      skin.color.set(appearance.skin);
      skinDetail.color.copy(skin.color).multiplyScalar(0.64);
      lips.color.copy(skin.color).lerp(new THREE.Color('#913f45'), 0.5);
    }
    if (appearance.hair) {
      hair.color.set(appearance.hair);
      hairHighlight.color.copy(hair.color).lerp(new THREE.Color('#bda18a'), 0.13);
    }
    if (appearance.shirt) {
      shirt.color.set(appearance.shirt);
      shirtTrim.color.copy(shirt.color).multiplyScalar(0.8);
    }
    if (appearance.eyes) iris.color.set(appearance.eyes);
    if (appearance.hairStyle && hairGroups[appearance.hairStyle]) {
      Object.entries(hairGroups).forEach(([style, group]) => { group.visible = style === appearance.hairStyle; });
    }
    if (appearance.glasses !== undefined) glasses.visible = Boolean(appearance.glasses);
    if (appearance.headWidth !== undefined) head.scale.x = clamp(appearance.headWidth, 0.85, 1.15);
  }

  function updateMouth(amount) {
    const width = 0.146 + expression * 0.027 - amount * 0.02;
    const open = 0.006 + amount * 0.107;
    const center = -0.315 - amount * 0.021;
    const curve = expression * 0.026;
    const surface = (x, y) => 0.465 * Math.sqrt(Math.max(0.01, 1 - (x / 0.546) ** 2 - (y / 0.76) ** 2)) + 0.013;
    mouthVertices[0] = 0;
    mouthVertices[1] = center;
    mouthVertices[2] = surface(0, center);
    for (let index = 0; index <= mouthSegments; index++) {
      const angle = index / mouthSegments * Math.PI * 2;
      const x = Math.cos(angle) * width;
      const y = center + Math.sin(angle) * open + (x / width) ** 2 * curve;
      const offset = (index + 1) * 3;
      mouthVertices[offset] = x;
      mouthVertices[offset + 1] = y;
      mouthVertices[offset + 2] = surface(x, y);
    }
    mouthGeometry.attributes.position.needsUpdate = true;
    mouthGeometry.computeVertexNormals();
    [upperLip, lowerLip].forEach((mesh, lipIndex) => {
      const attribute = mesh.geometry.attributes.position;
      const rest = lipRestPositions[lipIndex];
      for (let index = 0; index < attribute.count; index++) {
        const offset = index * 3;
        const t = clamp(rest[offset] / 0.16, -1, 1);
        const x = t * width;
        const arc = Math.sqrt(Math.max(0, 1 - t * t));
        const y = center + (lipIndex === 0 ? open : -open) * arc + t * t * curve;
        const referenceY = lipIndex === 0 ? -0.31 + 0.01 * t * t : -0.34 + 0.04 * t * t;
        const tubeOffsetY = rest[offset + 1] - referenceY;
        const tubeOffsetZ = rest[offset + 2] - (0.46 - 0.01 * t * t);
        attribute.setXYZ(index, x, y + tubeOffsetY, surface(x, y) + tubeOffsetZ + 0.006);
      }
      attribute.needsUpdate = true;
      mesh.geometry.computeVertexNormals();
    });
    teeth.visible = amount > 0.13;
    teeth.position.y = center + open * 0.52;
    teeth.position.z = surface(0, teeth.position.y) + 0.004;
    teeth.scale.x = width * 0.72;
    teeth.scale.y = Math.min(0.022, open * 0.26);
    tongue.visible = amount > 0.36;
    tongue.position.y = center - open * 0.66;
    tongue.position.z = surface(0, tongue.position.y) + 0.003;
  }

  function resetCamera() {
    camera.position.set(0.32, 2.38, 6.3);
    controls.target.set(0, 1.88, 0);
    controls.update();
    controls.saveState();
  }

  function render(timeSeconds = 0, pose = null) {
    if (disposed) return;
    const time = Number.isFinite(timeSeconds) ? timeSeconds : 0;
    const delta = previousTime === undefined ? 1 / 60 : Math.min(0.1, Math.max(0, time - previousTime));
    previousTime = time;
    energy += ((speaking ? targetEnergy : 0) - energy) * (1 - Math.exp(-delta * 17));
    const activity = speaking ? gesture : gesture * 0.2;
    body.position.y = Math.sin(time * 1.8) * 0.008;
    body.rotation.y = Math.sin(time * 0.58) * 0.022;
    headPivot.rotation.y = Math.sin(time * 0.69) * (0.035 + activity * 0.055);
    headPivot.rotation.x = Math.sin(time * 1.2) * 0.018 + Math.sin(time * 5.1) * energy * activity * 0.045;
    headPivot.rotation.z = Math.sin(time * 0.83) * 0.020;
    const blinkPhase = ((time + 1.3) % 4.65);
    const blink = blinkPhase < 0.18 ? Math.sin(blinkPhase / 0.18 * Math.PI) : 0;
    eyes.forEach((eye) => { eye.scale.y = 1 - blink * 0.94; });
    eyebrows.forEach(({ group, side }) => {
      group.position.y = 0.276 + expression * 0.012 + energy * 0.021;
      group.rotation.z = side * (expression - 0.5) * 0.10;
    });
    arms.forEach(({ arm, forearm, side }) => {
      arm.rotation.z = side * (0.11 + Math.sin(time * 0.95 + side) * 0.023 + activity * 0.10);
      arm.rotation.x = -activity * 0.12;
      forearm.rotation.x = -activity * (0.35 + Math.sin(time * 1.35 + side) * 0.25);
      forearm.rotation.z = -side * activity * 0.15;
    });
    if (pose) {
      body.position.y = 0;
      body.rotation.set(pose.body.x, pose.body.y, pose.body.z);
      headPivot.rotation.set(pose.headPivot.x, pose.headPivot.y, pose.headPivot.z);
      for (const { arm, forearm, side } of arms) {
        const part = pose.arms[side];
        arm.rotation.set(part.arm.x, part.arm.y, part.arm.z);
        forearm.rotation.set(part.forearm.x, part.forearm.y, part.forearm.z);
      }
      eyes.forEach(eye => { eye.scale.y = 1; });
    }
    updateMouth(pose ? 0 : energy);
    controls.update();
    renderer.render(scene, camera);
  }

  function resize(width, height) {
    if (!width || !height || disposed) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    controls.dispose();
    const geometries = new Set();
    const materials = new Set();
    scene.traverse((object) => {
      if (object.geometry) geometries.add(object.geometry);
      if (object.material) (Array.isArray(object.material) ? object.material : [object.material]).forEach((item) => materials.add(item));
    });
    geometries.forEach((geometry) => geometry.dispose());
    materials.forEach((item) => item.dispose());
    renderer.dispose();
  }

  updateAppearance({ hairStyle: 'swept' });
  resetCamera();
  updateMouth(0);
  return {
    updateAppearance,
    setExpression: (value) => { expression = clamp(value); },
    setEnergy: (value) => { targetEnergy = clamp(value); },
    setSpeaking: (value) => { speaking = Boolean(value); if (!speaking) targetEnergy = 0; },
    setGesture: (value) => { gesture = clamp(value); },
    resetCamera, render, resize, dispose, renderer, scene, camera,
  };
}
