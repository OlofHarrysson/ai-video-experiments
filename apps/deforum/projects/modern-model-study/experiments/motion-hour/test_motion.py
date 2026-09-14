"""Geometric checks for the time-bounded travelling shear wave."""

import unittest

import numpy as np

from deforum_lab.image.warps import mapping


class MotionTest(unittest.TestCase):
    def test_composed_mapping_has_exact_inverse(self):
        phrases = [
            {
                "start": 0,
                "duration": 3,
                "zoom": 0.3,
                "turn": 25,
                "travel": [0.1, -0.04],
            },
            {
                "kind": "wave",
                "start": 1,
                "duration": 5,
                "amplitude": 0.2,
                "wavelength": 0.8,
                "cycles": 1.5,
            },
        ]
        p = np.random.default_rng(22).uniform(0, 1.5, (300, 2))
        for t in [0, 1, 2, 3, 5, 6, 8]:
            np.testing.assert_allclose(
                mapping(mapping(p, t, phrases), t, phrases, True), p, atol=1e-12
            )

    def test_wave_returns_to_identity_and_moves_rows_differently(self):
        wave = [
            {
                "kind": "wave",
                "start": 0,
                "duration": 4,
                "amplitude": 0.2,
                "wavelength": 1,
                "cycles": 1,
            }
        ]
        p = np.array([[0.5, 0.25], [0.5, 0.75]])
        for t in [-1, 0, 4, 5]:
            np.testing.assert_array_equal(mapping(p, t, wave), p)
        q = mapping(p, 2, wave)
        self.assertLess(q[0, 0], p[0, 0])
        self.assertGreater(q[1, 0], p[1, 0])
        np.testing.assert_array_equal(q[:, 1], p[:, 1])


if __name__ == "__main__":
    unittest.main()
