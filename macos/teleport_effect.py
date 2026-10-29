import cv2
import numpy as np


ANIMATION_SECONDS = 0.65


def render_teleport(frame, background, mask, progress: float, returning: bool):
    progress = float(np.clip(progress, 0.0, 1.0))
    if progress >= 1.0:
        return frame.copy() if returning else background.copy()
    if progress <= 0.0:
        return background.copy() if returning else frame.copy()
    height, width = frame.shape[:2]
    silhouette = np.clip(mask, 0.0, 1.0).astype(np.float32)
    departure = 1.0 - progress if returning else progress
    visible = float(departure < 0.42)
    alpha = silhouette[..., None] * visible
    output = frame.astype(np.float32) * alpha + background.astype(np.float32) * (1 - alpha)
    streaks = np.zeros_like(frame)
    for column in range(0, width, max(5, width // 100)):
        offset = (column * 37) % max(1, height)
        position = int((offset - departure * height * 2.5) % height)
        length = max(12, int(height * (0.12 + ((column * 13) % 17) / 100)))
        cv2.line(streaks, (column, position), (column, position + length), (20, 20, 20), 4)
        cv2.line(streaks, (column, position), (column, position + length), (245, 245, 255), 1)
    expanded = cv2.dilate(silhouette, np.ones((13, 5), np.uint8))
    strength = float(np.sin(np.pi * progress) ** 0.5)
    streak_alpha = (np.any(streaks != 0, axis=2) * expanded * strength)[..., None]
    return np.clip(output * (1 - streak_alpha) + streaks * streak_alpha, 0, 255).astype(np.uint8)