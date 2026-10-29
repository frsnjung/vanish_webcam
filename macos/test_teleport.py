import unittest
from types import SimpleNamespace

from teleport import TeleportState, forehead_pose


class TeleportTests(unittest.TestCase):
    def test_requires_full_second_and_release_before_return(self):
        state = TeleportState()
        self.assertFalse(state.update(True, 0.0))
        self.assertFalse(state.update(True, 0.9))
        self.assertTrue(state.update(True, 1.0))
        self.assertTrue(state.vanished)
        self.assertFalse(state.update(True, 3.0))
        state.update(False, 3.1)
        state.update(False, 3.6)
        self.assertFalse(state.update(True, 4.0))
        self.assertTrue(state.update(True, 5.0))
        self.assertFalse(state.vanished)

    def test_broken_pose_resets_countdown(self):
        state = TeleportState()
        state.update(True, 0.0)
        state.update(False, 0.9)
        self.assertFalse(state.update(True, 1.0))
        self.assertFalse(state.update(True, 1.9))
        self.assertTrue(state.update(True, 2.0))

    def test_brief_detection_loss_does_not_rearm(self):
        state = TeleportState(armed=False, vanished=True)
        state.update(False, 0.0)
        self.assertFalse(state.update(True, 0.1))
        self.assertFalse(state.update(True, 2.0))
        self.assertTrue(state.vanished)

    def test_forehead_pose_rejects_missing_face_and_separated_fingers(self):
        face = [SimpleNamespace(x=0.5, y=0.5) for _ in range(478)]
        face[10] = SimpleNamespace(x=0.5, y=0.2)
        face[234] = SimpleNamespace(x=0.35, y=0.4)
        face[454] = SimpleNamespace(x=0.65, y=0.4)
        hand = [SimpleNamespace(x=0.5, y=0.6) for _ in range(21)]
        hand[9] = SimpleNamespace(x=0.5, y=0.45)
        for tip, joint, horizontal in ((8, 6, 0.49), (12, 10, 0.51)):
            hand[tip] = SimpleNamespace(x=horizontal, y=0.2)
            hand[joint] = SimpleNamespace(x=horizontal, y=0.35)
        for tip, joint in ((16, 14), (20, 18)):
            hand[tip] = SimpleNamespace(x=0.5, y=0.55)
            hand[joint] = SimpleNamespace(x=0.5, y=0.4)
        self.assertTrue(forehead_pose([hand], [face], 1280, 720))
        self.assertFalse(forehead_pose([hand], [], 1280, 720))
        hand[12] = SimpleNamespace(x=0.65, y=0.2)
        self.assertFalse(forehead_pose([hand], [face], 1280, 720))


if __name__ == "__main__":
    unittest.main()