"""Time-based radial transforms and composed motion phrases."""

import numpy as np

from .resampling import remap_rgb


def ease(t, start, end):
    u = np.clip((t - start) / (end - start), 0, 1)
    return u * u * (3 - 2 * u)


def transform(points, seconds, motion, inverse=False):
    """Invertible radial twist then similarity transform, in image-height units.

    Each phrase gives its total displacement; time controls its eased progress.
    Radial twist preserves radius, so negating its angle is the exact inverse.
    """
    center = np.array(motion.get("center", [0.75, 0.5]))
    progress = ease(seconds, 0, motion.get("settle", 2.5))
    late = ease(seconds, *motion.get("travel_window", [3.0, 6.0]))
    shift = np.array(motion.get("travel", [0, 0])) * late
    scale = 1 + motion.get("zoom", 0.12) * progress
    angle = np.deg2rad(motion.get("turn", 20)) * progress
    radius = motion.get("radius", 0.7)
    q = (points - center - shift) / scale if inverse else points - center
    theta = angle * np.exp(-np.sum(q * q, axis=-1) / (radius * radius))
    if inverse:
        theta = -theta
    c, s = np.cos(theta), np.sin(theta)
    rotated = np.stack(
        [q[..., 0] * c - q[..., 1] * s, q[..., 0] * s + q[..., 1] * c], -1
    )
    return center + rotated if inverse else center + rotated * scale + shift


def mapping(points, seconds, phrases, inverse=False):
    selected = reversed(phrases) if inverse else phrases
    for phrase in selected:
        if phrase.get("kind") not in (
            None,
            "cruise",
            "plane",
            "shear",
            "wave",
            "continuation",
        ):
            raise ValueError(f"Unknown spatial effect: {phrase['kind']}")
        if phrase.get("kind") == "continuation":
            # Hermite path in translation, log scale and radians. Its first
            # derivative is explicit so a branch can retain the incoming speed.
            duration = phrase["duration"]
            if duration <= 0:
                raise ValueError("Continuation duration must be positive")
            elapsed = max(0.0, seconds - phrase["start"])
            u = min(1.0, elapsed / duration)
            end = np.asarray(phrase["end"], dtype=float)
            v0 = np.asarray(phrase["velocity_start"], dtype=float)
            v1 = np.asarray(phrase["velocity_end"], dtype=float)
            state = (
                (-2 * u**3 + 3 * u * u) * end
                + (u**3 - 2 * u * u + u) * duration * v0
                + (u**3 - u * u) * duration * v1
                + max(0.0, elapsed - duration) * v1
            )
            center = np.asarray(phrase["center"])
            scale = np.exp(state[2])
            q = (points - center - state[:2]) / scale if inverse else points - center
            angle = -state[3] if inverse else state[3]
            c, s = np.cos(angle), np.sin(angle)
            q = np.stack(
                [c * q[..., 0] - s * q[..., 1], s * q[..., 0] + c * q[..., 1]], -1
            )
            points = center + q if inverse else center + scale * q + state[:2]
            continue
        if phrase.get("kind") == "cruise":
            # A constant underlying velocity can carry motion through phrase joins.
            t = max(0.0, seconds - phrase.get("start", 0.0))
            center = np.array(phrase.get("center", [0.75, 0.5]))
            shift = t * np.array(phrase.get("velocity", [0, 0]))
            scale = np.exp(t * phrase.get("log_zoom_rate", 0))
            angle = np.deg2rad(t * phrase.get("roll_rate", 0))
            q = (points - center - shift) / scale if inverse else points - center
            if inverse:
                angle = -angle
            c, s = np.cos(angle), np.sin(angle)
            q = np.stack(
                [c * q[..., 0] - s * q[..., 1], s * q[..., 0] + c * q[..., 1]], -1
            )
            points = center + q if inverse else center + q * scale + shift
            continue
        if phrase.get("kind") == "plane":
            # Project a flat sheet rotated about its x/y axes, not a depth scene.
            progress = ease(
                seconds, phrase["start"], phrase["start"] + phrase["duration"]
            )
            ax, ay = np.deg2rad(np.array(phrase.get("tilt", [0, 0])) * progress)
            cx, sx, cy, sy = np.cos(ax), np.sin(ax), np.cos(ay), np.sin(ay)
            distance = phrase.get("distance", 2.0)
            matrix = np.array(
                [[cy, sy * sx, 0], [0, cx, 0], [-sy / distance, cy * sx / distance, 1]]
            )
            if inverse:
                matrix = np.linalg.inv(matrix)
            center = np.array(phrase.get("center", [0.75, 0.5]))
            q = points - center
            homogeneous = np.concatenate([q, np.ones_like(q[..., :1])], axis=-1)
            # Avoid the macOS BLAS batched-matmul path for full-size image grids.
            h = np.einsum("...j,ij->...i", homogeneous, matrix, optimize=False)
            if np.any(np.abs(h[..., 2]) < 1e-6):
                raise ValueError("Plane turn reaches the projective horizon")
            points = center + h[..., :2] / h[..., 2:]
            continue
        if phrase.get("kind") == "shear":
            progress = ease(
                seconds, phrase["start"], phrase["start"] + phrase["duration"]
            )
            points = points.copy()
            offset = (
                phrase["amount"]
                * progress
                * (points[..., 1] - phrase.get("center_y", 0.5))
            )
            points[..., 0] += -offset if inverse else offset
            continue
        if phrase.get("kind") == "wave":
            # Displacement depends only on the other axis, so inversion is exact.
            u = (seconds - phrase["start"]) / phrase["duration"]
            if 0 < u < 1:
                envelope = np.sin(np.pi * u) ** 2
                axis = 1 if phrase.get("axis") == "vertical" else 0
                offset = (
                    phrase["amplitude"]
                    * envelope
                    * np.sin(
                        2
                        * np.pi
                        * (
                            points[..., 1 - axis] / phrase["wavelength"]
                            - phrase["cycles"] * u
                        )
                        + phrase.get("phase", 0)
                    )
                )
                points = points.copy()
                points[..., axis] += -offset if inverse else offset
            continue
        motion = {
            **phrase,
            "settle": phrase["duration"],
            "travel_window": [0, phrase["duration"]],
        }
        points = transform(points, max(0.0, seconds - phrase["start"]), motion, inverse)
    return points


def warp_at_time(rgb, start, end, phrases):
    if start == end:
        return rgb.copy()
    h, w = rgb.shape[:2]
    y, x = np.mgrid[:h, :w].astype(np.float32)
    points = np.stack([x / h, y / h], -1)
    coords = mapping(mapping(points, end, phrases, True), start, phrases) * h
    return remap_rgb(rgb, coords.astype(np.float32))
