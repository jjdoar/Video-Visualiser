import cv2
import numpy as np

from typing import Protocol


class Mode(Protocol):
    def __init__(self):
        ...

    def apply(frame):
        ...


class Original(Mode):
    def __init__(self):
        pass

    def apply(self, frame):
        if frame is None:
            return

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


class Grayscale(Mode):
    def __init__(self):
        pass

    def apply(self, frame):
        if frame is None:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)


class Difference(Mode):
    def __init__(self):
        self.prev_frame = None

    def apply(self, frame):
        if frame is None:
            self.prev_frame = None
            return

        if self.prev_frame is None:
            self.prev_frame = frame
            return None

        frame_diff = cv2.absdiff(frame, self.prev_frame)
        self.prev_frame = frame

        return frame_diff


class Motion(Mode):
    def __init__(self):
        self.prev_gray = None

    def apply(self, frame):
        # VERY POOR PERFORMANCE
        if frame is None:
            self.prev_gray = None
            return

        if self.prev_gray is None:
            self.prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_motion = cv2.calcOpticalFlowFarneback(
            self.prev_gray, frame_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        self.prev_gray = frame_gray

        angle = np.arctan2(frame_motion[..., 1], frame_motion[..., 0])
        magnitude = np.sqrt(frame_motion[..., 0] ** 2 + frame_motion[..., 1] ** 2)
        normalized_magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

        hsv = np.zeros((frame_gray.shape[0], frame_gray.shape[1], 3), dtype=np.float32)
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 1] = 255
        hsv[..., 2] = normalized_magnitude

        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
