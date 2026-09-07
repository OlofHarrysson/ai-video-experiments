import unittest
import numpy as np
from walkthrough import graph, warp


class MotionTests(unittest.TestCase):
    def test_zero_displacement_preserves_every_pixel(self):
        image = np.random.default_rng(2).integers(0, 256, (32, 64, 3), dtype=np.uint8)
        self.assertTrue(np.array_equal(image, warp(image, np.zeros((32, 64, 2), np.float32))))

    def test_forward_arrow_moves_feature_in_that_direction(self):
        image = np.zeros((32, 64, 3), np.uint8)
        image[15, 20] = 255
        flow = np.zeros((32, 64, 2), np.float32)
        flow[..., 0], flow[..., 1] = 5, 2.5
        result = warp(image, flow, 0.8)
        self.assertTrue(np.array_equal(result[17, 24], [255, 255, 255]))
        self.assertTrue(np.array_equal(result[15, 20], [0, 0, 0]))

    def test_comparisons_change_only_crop(self):
        for artwork in ('marsh', 'portal'):
            g = graph(artwork)
            samples = [v['inputs'] for v in g.values() if v['class_type'] == 'KSampler']
            settings = [{k:v for k,v in s.items() if k != 'latent_image'} for s in samples]
            self.assertEqual(len(samples), 3)
            self.assertEqual(settings[0], settings[1])
            self.assertEqual(settings[1], settings[2])
            crops = [v['inputs']['x'] for v in g.values() if v['class_type'] == 'ImageCrop']
            self.assertEqual(crops, [0, 1024, 2048])


if __name__ == '__main__':
    unittest.main()
