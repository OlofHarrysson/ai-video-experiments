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
        if phrase.get("kind") == "wave":
            # Horizontal displacement depends only on y, so its inverse is exact.
            u = (seconds - phrase["start"]) / phrase["duration"]
            if 0 < u < 1:
                envelope = np.sin(np.pi * u) ** 2
                offset = (
                    phrase["amplitude"]
                    * envelope
                    * np.sin(
                        2
                        * np.pi
                        * (points[..., 1] / phrase["wavelength"] - phrase["cycles"] * u)
                        + phrase.get("phase", 0)
                    )
                )
                points = points.copy()
                points[..., 0] += -offset if inverse else offset
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
