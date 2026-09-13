import unittest
import numpy as np
from noise_sequence import noise_at


class NoiseSequenceTest(unittest.TestCase):
    @staticmethod
    def prepare(shape, seed):
        return np.random.default_rng(seed).standard_normal(shape).astype(np.float32)

    def test_endpoints_and_resume(self):
        shape = (1000,)
        for rho in (0., .85, 1.):
            np.testing.assert_array_equal(noise_at(self.prepare, shape, 10, 0, rho), self.prepare(shape, 10))
        np.testing.assert_array_equal(noise_at(self.prepare, shape, 10, 8, 0), self.prepare(shape, 18))
        np.testing.assert_array_equal(noise_at(self.prepare, shape, 10, 8, 1), self.prepare(shape, 10))
        n7 = noise_at(self.prepare, shape, 10, 7, .85)
        n8 = noise_at(self.prepare, shape, 10, 8, .85)
        np.testing.assert_allclose(n8, .85*n7 + np.sqrt(1-.85**2)*self.prepare(shape, 18), atol=2e-7, rtol=1e-6)
        np.testing.assert_array_equal(n8, noise_at(self.prepare, shape, 10, 8, .85))

    def test_variance_and_correlation(self):
        shape = (200000,)
        for rho in (0., .85):
            prev = noise_at(self.prepare, shape, 10, 6, rho)
            curr = noise_at(self.prepare, shape, 10, 7, rho)
            self.assertAlmostEqual(float(curr.std()), 1., delta=.01)
            self.assertAlmostEqual(float(curr.mean()), 0., delta=.01)
            self.assertAlmostEqual(float(np.corrcoef(prev, curr)[0, 1]), rho, delta=.01)

    def test_invalid_inputs(self):
        for index, rho in ((-1, .5), (1.2, .5), (1, 1.01)):
            with self.assertRaises(ValueError):
                noise_at(self.prepare, (1,), 10, index, rho)


if __name__ == '__main__':
    unittest.main()
