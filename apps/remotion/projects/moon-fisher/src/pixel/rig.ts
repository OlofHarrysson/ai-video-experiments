import type { Shape, Vec2 } from "./shapes";

// A skeleton for posing drawn characters. Parts are drawn once, in a rest
// pose; each part rides on one bone, and a pose is a set of bone angles.

// Where a bone starts, and the direction it points, in radians.
export type Frame = { x: number; y: number; a: number };

// A bone in the rest pose: from `start` to `end`, relative to the root.
export type BoneDef = { parent: string | null; start: Vec2; end: Vec2 };

type Bone = {
  name: string;
  parent: string | null;
  // Where the bone starts: in its parent's frame, or relative to the root.
  attach: Vec2;
  len: number;
  rest: Frame;
};

export type Rig = { bones: Bone[]; rest: Record<string, Frame> };

export const toLocal = (f: Frame, [x, y]: Vec2): Vec2 => {
  const dx = x - f.x;
  const dy = y - f.y;
  const c = Math.cos(f.a);
  const s = Math.sin(f.a);
  return [dx * c + dy * s, -dx * s + dy * c];
};

export const toWorld = (f: Frame, [u, v]: Vec2): Vec2 => {
  const c = Math.cos(f.a);
  const s = Math.sin(f.a);
  return [f.x + u * c - v * s, f.y + u * s + v * c];
};

// Bones must be listed after their parents.
export const buildRig = (defs: Record<string, BoneDef>): Rig => {
  const bones: Bone[] = [];
  const rest: Record<string, Frame> = {};
  for (const [name, d] of Object.entries(defs)) {
    const dx = d.end[0] - d.start[0];
    const dy = d.end[1] - d.start[1];
    const frame = { x: d.start[0], y: d.start[1], a: Math.atan2(dy, dx) };
    if (d.parent && !rest[d.parent]) {
      throw new Error(`Bone ${name} is listed before its parent ${d.parent}`);
    }
    bones.push({
      name,
      parent: d.parent,
      attach: d.parent ? toLocal(rest[d.parent], d.start) : d.start,
      len: Math.hypot(dx, dy),
      rest: frame,
    });
    rest[name] = frame;
  }
  return { bones, rest };
};

// Angles are absolute, in degrees, so a pose reads as directions on screen:
// 0 points right, 90 down, -90 up. A child still moves with its parent's
// joint. Bones without an angle keep their rest direction.
export type Angles = Partial<Record<string, number>>;

export const poseRig = (
  rig: Rig,
  root: Vec2,
  angles: Angles,
): Record<string, Frame> => {
  const frames: Record<string, Frame> = {};
  for (const b of rig.bones) {
    const deg = angles[b.name];
    const a = deg === undefined ? b.rest.a : (deg * Math.PI) / 180;
    const [x, y] = b.parent
      ? toWorld(frames[b.parent], b.attach)
      : [root[0] + b.attach[0], root[1] + b.attach[1]];
    frames[b.name] = { x, y, a };
  }
  return frames;
};

// The end of a posed bone, such as the grip of a hand.
export const boneEnd = (
  rig: Rig,
  frames: Record<string, Frame>,
  name: string,
): Vec2 => {
  const bone = rig.bones.find((b) => b.name === name);
  if (!bone) throw new Error(`No bone ${name}`);
  return toWorld(frames[name], [bone.len, 0]);
};

// Carry a shape drawn in the rest pose onto its posed bone.
export const moveShape = (s: Shape, from: Frame, to: Frame): Shape => {
  const p = (v: Vec2): Vec2 => toWorld(to, toLocal(from, v));
  switch (s.kind) {
    case "ellipse": {
      const [cx, cy] = p([s.cx, s.cy]);
      return { ...s, cx, cy, rot: s.rot + to.a - from.a };
    }
    case "capsule":
      return { ...s, a: p(s.a), b: p(s.b) };
    case "poly":
      return { ...s, pts: s.pts.map(p) };
    case "blend":
      return { ...s, shapes: s.shapes.map((c) => moveShape(c, from, to)) };
  }
};
