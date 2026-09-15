import unittest

import numpy as np

from deforum_lab.image.warps import mapping


class MotionTests(unittest.TestCase):
    def setUp(self):
        y, x = np.mgrid[0.1:0.9:13j, 0.1:1.4:19j]
        self.p = np.stack([x, y], -1)
        self.phrases = [
            {"kind": "cruise", "start": -1, "velocity": [0.04, -0.01], "roll_rate": 2},
            {
                "kind": "plane",
                "start": 0,
                "duration": 5,
                "tilt": [22, -28],
                "distance": 2.5,
            },
            {"kind": "shear", "start": 1, "duration": 4, "amount": 0.25},
            {
                "kind": "wave",
                "start": 1,
                "duration": 6,
                "amplitude": 0.07,
                "wavelength": 1.1,
                "cycles": 0.8,
                "axis": "vertical",
            },
        ]

    def test_composed_inverse(self):
        for t in np.linspace(0, 8, 25):
            np.testing.assert_allclose(
                mapping(mapping(self.p, t, self.phrases), t, self.phrases, True),
                self.p,
                atol=1e-10,
            )

    def test_motion_carries_past_completed_events(self):
        for t in (0, 1, 5, 7, 8):
            self.assertGreater(
                np.median(
                    np.linalg.norm(
                        mapping(self.p, t + 0.01, self.phrases)
                        - mapping(self.p, t, self.phrases),
                        axis=-1,
                    )
                ),
                1e-5,
            )

    def test_relative_map_independent_of_frame_rate(self):
        q = self.p
        for i in range(24):
            q = mapping(
                mapping(q, i / 24, self.phrases, True), (i + 1) / 24, self.phrases
            )
        direct = mapping(mapping(self.p, 0, self.phrases, True), 1, self.phrases)
        np.testing.assert_allclose(q, direct, atol=1e-10)

    def test_full_resolution_plane(self):
        y, x = np.mgrid[:1024, :1536].astype(np.float32)
        points = np.stack([x / 1024, y / 1024], -1)
        result = mapping(points, 3, self.phrases[1:2])
        self.assertEqual(result.shape, points.shape)
        self.assertTrue(np.isfinite(result).all())
        np.testing.assert_allclose(
            mapping(result, 3, self.phrases[1:2], True), points, atol=1e-10
        )

    def test_unknown_effect_fails(self):
        with self.assertRaisesRegex(ValueError, "Unknown spatial effect"):
            mapping(self.p, 1, [{"kind": "not-supported"}])

    def test_plane_identity(self):
        np.testing.assert_allclose(
            mapping(self.p, 0, self.phrases[1:2]), self.p, atol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
