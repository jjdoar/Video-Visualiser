from typing import Protocol
import cv2


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

        frame_copy = frame.copy()
        frame = cv2.absdiff(frame, self.prev_frame)
        self.prev_frame = frame_copy

        return frame
