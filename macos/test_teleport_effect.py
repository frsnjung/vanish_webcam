import unittest

import numpy as np

from teleport_effect import render_teleport


class AnimationTests(unittest.TestCase):
    def setUp(self):
        self.background = np.full((120, 160, 3), 60, dtype=np.uint8)
        self.frame = self.background.copy()
        self.frame[20:100, 50:110] = 180
        self.mask = np.zeros((120, 160), dtype=np.float32)
        self.mask[20:100, 50:110] = 1

    def test_departure_endpoints(self):
        for progress, expected in ((0, self.frame), (1, self.background)):
            np.testing.assert_array_equal(
                render_teleport(self.frame, self.background, self.mask, progress, False), expected
            )

    def test_return_endpoints(self):
        for progress, expected in ((0, self.background), (1, self.frame)):
            np.testing.assert_array_equal(
                render_teleport(self.frame, self.background, self.mask, progress, True), expected
            )

    def test_streaks_move_and_preserve_distant_background(self):
        first = render_teleport(self.frame, self.background, self.mask, 0.25, False)
        second = render_teleport(self.frame, self.background, self.mask, 0.35, False)
        self.assertFalse(np.array_equal(first, second))
        np.testing.assert_array_equal(first[:, :40], self.background[:, :40])
        self.assertEqual(first.dtype, np.uint8)
        self.assertEqual(first.shape, self.frame.shape)

    def test_return_reverses_departure(self):
        np.testing.assert_array_equal(
            render_teleport(self.frame, self.background, self.mask, 0.25, True),
            render_teleport(self.frame, self.background, self.mask, 0.75, False),
        )


if __name__ == "__main__":
    unittest.main()