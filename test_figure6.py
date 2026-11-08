"""Checks specific to the selected reproductive/population four-panel figure."""
import unittest
import numpy as np
from models import (reproductive_output as G, reproductive_threshold,
                    population_threshold, population_equilibrium)


class Figure6Checks(unittest.TestCase):
    def test_reproductive_limits(self):
        self.assertEqual(G(0, 10, 0), 1)
        self.assertEqual(G(.5, 0, 0), 1)
        self.assertEqual(G(.5, 10, 1), 1)

    def test_reproductive_contours(self):
        for target in [.5, .75, .9, .95]:
            c = .5
            r = float(reproductive_threshold(c, 0, target))
            self.assertAlmostEqual(float(1-G(c, r, 0)), target)
        self.assertAlmostEqual(float(100*(1-G(.5, 10, 0))), 100*5/6)

    def test_population_examples(self):
        self.assertAlmostEqual(float(population_threshold(.5, 0, 4, .01)), 5.94)
        self.assertAlmostEqual(float(population_threshold(.5, 0, 10, .01)), 17.82)
        self.assertAlmostEqual(float(population_threshold(.5, .05, 4, .01)), 2.97/(.5*.8015))

    def test_population_feasibility_boundary(self):
        fmax = 1/3.97
        self.assertTrue(np.isinf(population_threshold(.5, fmax, 4, .01)))
        self.assertTrue(np.isinf(population_threshold(.5, fmax+1e-6, 4, .01)))
        self.assertTrue(np.isfinite(population_threshold(.5, fmax-1e-6, 4, .01)))
        self.assertTrue(np.isinf(population_threshold(0, 0, 4, .01)))
        self.assertTrue(np.isinf(reproductive_threshold(.5, .05, .95)))

    def test_randomized_adult_targets(self):
        rng = np.random.default_rng(20261108)
        for _ in range(1000):
            R0 = rng.uniform(2, 10)
            c = rng.uniform(.001, 1)
            H = R0-.01*(R0-1)
            f = rng.uniform(0, 1/H-.00001)
            r = float(population_threshold(c, f, R0, .01))
            g = G(c, r, f)
            self.assertAlmostEqual(float(population_equilibrium(g, R0)), .01)
            self.assertGreater(population_equilibrium(G(c, r*.99, f), R0), .01)
            self.assertLess(population_equilibrium(G(c, r*1.01, f), R0), .01)
            next_f = R0*g*.01/(1+(R0-1)*g*.01)
            self.assertAlmostEqual(float(next_f), .01)

    def test_growth_sweep_formula(self):
        c = np.array([.01, .25, .5, 1])[:, None]
        R0 = np.array([2, 4, 6, 8, 10])[None, :]
        np.testing.assert_allclose(population_threshold(c, 0, R0, .01), .99*(R0-1)/c)

    def test_response_directions(self):
        self.assertLess(G(.6, 10, .05), G(.5, 10, .05))
        self.assertGreater(G(.5, 10, .06), G(.5, 10, .05))
        self.assertGreater(population_threshold(.5, .05, 4, .01), population_threshold(.5, 0, 4, .01))
        self.assertGreater(population_threshold(.5, 0, 5, .01), population_threshold(.5, 0, 4, .01))

    def test_input_domains(self):
        for call in [lambda: G(-1, 1, 0), lambda: G(1, -1, 0),
                     lambda: G(1, 1, 2), lambda: G(np.nan, 1, 0),
                     lambda: population_threshold(1, 0, 1, .01),
                     lambda: population_threshold(1, 0, 4, 0)]:
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
