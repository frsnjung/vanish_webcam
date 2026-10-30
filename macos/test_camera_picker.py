import subprocess
import unittest
from unittest.mock import patch

from camera_picker import choose_camera


class CameraPickerTests(unittest.TestCase):
    @patch("camera_picker.subprocess.run")
    @patch("builtins.input", side_effect=["", "-1", "3", "abc", "1"])
    def test_selects_listed_camera_after_invalid_input(self, prompt, run):
        run.return_value.stdout = '["MacBook Pro Camera", "USB Camera", "OBS Virtual Camera"]'
        self.assertEqual(choose_camera(), 1)

    @patch("camera_picker.subprocess.run")
    @patch("builtins.input", return_value="q")
    def test_cancel(self, prompt, run):
        run.return_value.stdout = '["MacBook Pro Camera"]'
        with self.assertRaises(SystemExit) as result:
            choose_camera()
        self.assertEqual(result.exception.code, 0)

    @patch("camera_picker.subprocess.run", side_effect=subprocess.TimeoutExpired("swift", 30))
    @patch("builtins.input")
    def test_refuses_unfiltered_selection_when_enumeration_unavailable(self, prompt, run):
        with self.assertRaisesRegex(RuntimeError, "Cannot list camera names safely"):
            choose_camera()
        prompt.assert_not_called()

    @patch("camera_picker.subprocess.run")
    @patch("builtins.input", side_effect=["1", "2"])
    @patch("builtins.print")
    def test_hides_obs_rejects_its_index_and_preserves_physical_indices(self, output, prompt, run):
        run.return_value.stdout = '["MacBook Pro Camera", "OBS Virtual Camera", "USB Camera"]'
        self.assertEqual(choose_camera(), 2)
        self.assertEqual(prompt.call_count, 2)
        self.assertFalse(any("OBS Virtual Camera" in str(call) for call in output.call_args_list))

    @patch("camera_picker.subprocess.run")
    def test_only_obs_has_no_selectable_devices(self, run):
        run.return_value.stdout = '["obs virtual camera"]'
        with self.assertRaisesRegex(RuntimeError, "No selectable cameras"):
            choose_camera()

    @patch("camera_picker.subprocess.run")
    def test_no_devices(self, run):
        run.return_value.stdout = "[]"
        with self.assertRaisesRegex(RuntimeError, "No video cameras"):
            choose_camera()


if __name__ == "__main__":
    unittest.main()