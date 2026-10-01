"""Geometric invariants for authored inverse image motion."""

import unittest

import numpy as np

from deforum_lab.image.landmarks import landmark_maps, warp_landmarks


class LandmarkWarpTests(unittest.TestCase):
    def test_identity_preserves_pixels(self):
        y, x = np.mgrid[:96, :160]
        pixels = np.stack([x, y, (x + y) % 255], axis=-1).astype(np.uint8)
        points = [[0, 0], [159, 0], [0, 95], [159, 95], [80, 48]]
        result, diagnostics = warp_landmarks(pixels, points, points)
        np.testing.assert_array_equal(result, pixels)
        self.assertEqual(diagnostics["folded_pixel_fraction"], 0)

    def test_translation_uses_inverse_coordinates(self):
        points = np.asarray([[0, 0], [159, 0], [0, 95], [159, 95], [80, 48]])
        mx, my = landmark_maps(points, points + [7, -4], 160, 96)
        y, x = np.mgrid[:96, :160]
        np.testing.assert_allclose(mx, x - 7, atol=.001)
        np.testing.assert_allclose(my, y + 4, atol=.001)


if __name__ == "__main__":
    unittest.main()
