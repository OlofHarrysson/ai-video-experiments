"""Smooth inverse image deformation from explicit corresponding landmarks."""

import cv2
import numpy as np


def landmark_maps(before, after, width, height, *, grid_step=16, regularization=1e-3):
    """Fit target-to-source thin-plate displacement, with caller-supplied fixed pins.

    Positions are pixel coordinates. This transports nearby pixels too; it is not
    semantic tracking or an object-boundary protection mask.
    """
    source, target = np.asarray(before, float), np.asarray(after, float)
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 2:
        raise ValueError("Expected matching Nx2 source and target landmarks")
    if not np.isfinite(source).all() or not np.isfinite(target).all():
        raise ValueError("Landmarks must be finite")
    # Merge coincident destination handles so shared contour vertices do not
    # make the interpolation system singular.
    _, unique, inverse = np.unique(
        np.round(target, 2), axis=0, return_index=True, return_inverse=True
    )
    controls = target[unique] / width
    displacement = np.zeros_like(controls)
    for i in range(len(controls)):
        displacement[i] = ((source - target)[inverse == i]).mean(axis=0) / width

    def kernel(a, b):
        r2 = ((a[:, None] - b[None]) ** 2).sum(axis=2)
        return 0.5 * r2 * np.log(np.maximum(r2, 1e-20))

    n = len(controls)
    affine = np.c_[np.ones(n), controls]
    system = np.block(
        [
            [kernel(controls, controls) + regularization * np.eye(n), affine],
            [affine.T, np.zeros((3, 3))],
        ]
    )
    weights = np.linalg.solve(system, np.r_[displacement, np.zeros((3, 2))])
    gx = np.linspace(0, width - 1, (width - 1) // grid_step + 2)
    gy = np.linspace(0, height - 1, (height - 1) // grid_step + 2)
    xx, yy = np.meshgrid(gx, gy)
    points = np.c_[xx.ravel(), yy.ravel()] / width
    delta = (
        kernel(points, controls) @ weights[:n]
        + np.c_[np.ones(len(points)), points] @ weights[n:]
    ) * width
    delta = delta.reshape(len(gy), len(gx), 2).astype(np.float32)
    # Remap the low-resolution displacement on matching endpoint coordinates.
    yy_full, xx_full = np.mgrid[:height, :width].astype(np.float32)
    low_x = xx_full * (len(gx) - 1) / (width - 1)
    low_y = yy_full * (len(gy) - 1) / (height - 1)
    dense = cv2.remap(
        delta, low_x, low_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )
    return xx_full + dense[..., 0], yy_full + dense[..., 1]


def warp_landmarks(image, before, after):
    """Return transported RGB pixels and field diagnostics."""
    height, width = image.shape[:2]
    mx, my = landmark_maps(before, after, width, height)
    dx_y, dx_x = np.gradient(mx)
    dy_y, dy_x = np.gradient(my)
    determinant = dx_x * dy_y - dx_y * dy_x
    result = cv2.remap(
        image, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101
    )
    return result, {
        "min_jacobian": float(determinant.min()),
        "folded_pixel_fraction": float((determinant <= 0).mean()),
    }
