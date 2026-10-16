import { Vector3 } from "three";

/** A camera placement: where it is, what it looks at, its roll and vertical field of view. */
export type Shot = { position: Vector3; target: Vector3; roll: number; fov: number };
