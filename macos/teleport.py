import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import vanish_cam as app
from vanish_sound import VanishSound
from teleport_effect import ANIMATION_SECONDS, render_teleport
from camera_picker import choose_camera


def forehead_pose(hands, faces, width: int, height: int) -> bool:
    if not faces:
        return False
    face = faces[0]
    forehead = np.array((face[10].x * width, face[10].y * height))
    face_width = abs(face[454].x - face[234].x) * width
    if face_width < 1:
        return False
    for hand in hands:
        points = np.array([(point.x * width, point.y * height) for point in hand])
        palm_length = np.linalg.norm(points[9] - points[0])
        if palm_length < 1:
            continue
        extended = all(
            np.linalg.norm(points[tip] - points[0])
            > np.linalg.norm(points[joint] - points[0]) * 1.15
            for tip, joint in ((8, 6), (12, 10))
        )
        folded = all(
            np.linalg.norm(points[tip] - points[0])
            < np.linalg.norm(points[joint] - points[0]) * 1.15
            for tip, joint in ((16, 14), (20, 18))
        )
        together = np.linalg.norm(points[8] - points[12]) < palm_length * 0.6
        nearby = all(
            np.linalg.norm(points[tip] - forehead) < face_width * 0.5
            for tip in (8, 12)
        )
        if extended and folded and together and nearby:
            return True
    return False


@dataclass
class TeleportState:
    vanished: bool = False
    hold_started: float | None = None
    release_started: float | None = None
    armed: bool = True

    def update(self, pose: bool, now: float) -> bool:
        if not pose:
            self.hold_started = None
            if self.release_started is None:
                self.release_started = now
            if now - self.release_started >= 0.4:
                self.armed = True
            return False
        self.release_started = None
        if not self.armed:
            return False
        if self.hold_started is None:
            self.hold_started = now
        if now - self.hold_started < 1.0:
            return False
        self.vanished = not self.vanished
        self.armed = False
        self.hold_started = None
        return True


def create_trackers(resources: ExitStack):
    face = vision.FaceLandmarker.create_from_options(
        vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(
                model_asset_path=str(app.APP_DIR / "face_landmarker.task")
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
        )
    )
    resources.callback(face.close)
    hand = vision.HandLandmarker.create_from_options(
        vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(app.HAND_MODEL)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.35,
            min_hand_presence_confidence=0.35,
            min_tracking_confidence=0.45,
        )
    )
    resources.callback(hand.close)
    return face, hand


def run() -> None:
    parser = argparse.ArgumentParser(description="Animated Goku-style teleport for Teams")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--camera", type=int, help="Camera index; omit to choose interactively")
    args = parser.parse_args()
    camera_index = args.camera
    if not args.self_test and camera_index is None:
        camera_index = choose_camera()
    with ExitStack() as resources:
        sound = VanishSound(Path(__file__).resolve().parent / "teleport.wav")
        resources.callback(sound.close)
        face, hand = create_trackers(resources)
        segmenter = vision.ImageSegmenter.create_from_options(
            vision.ImageSegmenterOptions(
                base_options=python.BaseOptions(model_asset_path=str(app.SEGMENTER_MODEL)),
                running_mode=vision.RunningMode.VIDEO,
                output_confidence_masks=True,
                output_category_mask=False,
            )
        )
        resources.callback(segmenter.close)
        if args.self_test:
            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=np.zeros((720, 1280, 3), dtype=np.uint8),
            )
            face.detect_for_video(image, 0)
            hand.detect_for_video(image, 0)
            mask = app.person_mask(segmenter, image, 0, 1280, 720)
            test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            for returning in (False, True):
                for progress in (0.0, 0.25, 0.5, 0.75, 1.0):
                    render_teleport(test_frame, test_frame, mask, progress, returning)
            print("Audio decoded; face, hand, segmentation, and both animations passed self-test.")
            return
        capture = app.open_camera(camera_index, 1280, 720)
        resources.callback(capture.release)
        resources.callback(cv2.destroyAllWindows)
        cv2.namedWindow("VanishCam - Animated Goku", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("VanishCam - Animated Goku", 960, 540)
        state = TeleportState()
        animation_started = None
        animation_frame = None
        animation_mask = None
        background = None
        samples = []
        started = time.monotonic()
        calibration_started = started
        last_detection = -1.0
        camera = None
        print("Step out of view for four seconds. Keep the camera still.")
        print("Hold two fingers together at your forehead for one second to teleport.")
        print("Lower your hand, then repeat to return. R returns; Space recalibrates; Q quits.")
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError("The webcam stopped returning frames.")
            height, width = frame.shape[:2]
            if camera is None:
                options = argparse.Namespace(
                    virtual_camera=True, virtual_backend="obs", virtual_device=None, fps=30
                )
                camera = app.open_virtual_camera(options, width, height)
                resources.callback(camera.close)
            now = time.monotonic()
            if background is None:
                if now - calibration_started >= 3.45:
                    samples.append(frame.copy())
                if now - calibration_started >= 4.0:
                    background = np.median(np.stack(samples[-18:]), axis=0).astype(np.uint8)
                    samples.clear()
                    print("Background ready. You can step back into view.")
            elif now - last_detection >= 0.1:
                last_detection = now
                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                )
                timestamp = int((now - started) * 1000)
                faces = face.detect_for_video(image, timestamp).face_landmarks
                hands = hand.detect_for_video(image, timestamp).hand_landmarks
                if state.update(forehead_pose(hands, faces, width, height), now):
                    animation_frame = frame.copy()
                    animation_mask = app.person_mask(segmenter, image, timestamp, width, height)
                    animation_started = time.monotonic()
                    sound.play()
                    print("Teleported away." if state.vanished else "Returned.")
            display = background if state.vanished and background is not None else frame
            if animation_started is not None:
                progress = (time.monotonic() - animation_started) / ANIMATION_SECONDS
                if progress < 1.0:
                    display = render_teleport(
                        animation_frame, background, animation_mask, progress, not state.vanished
                    )
                else:
                    animation_started = None
            app.send_virtual_frame(camera, display)
            cv2.imshow("VanishCam - Animated Goku", display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("r"):
                state = TeleportState(armed=False)
                animation_started = None
            if key == ord(" "):
                background = None
                animation_started = None
                samples.clear()
                calibration_started = now
                state = TeleportState()
                print("Step out of view for four seconds.")
            camera.sleep_until_next_frame()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass