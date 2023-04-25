import logging
import sys
import cv2

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QCheckBox,
    QComboBox,
    QLineEdit,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer


class VideoApp(QMainWindow):
    def __init__(self, default_width=800, default_height=600) -> None:
        super().__init__()
        self.resize(default_width, default_height)
        self.setWindowTitle("Video Visualizer")

        # UI elements
        self.video_label = QLabel(self)
        self.open_button = QPushButton("Open", self)
        self.play_button = QPushButton("Play", self)
        self.pause_button = QPushButton("Pause", self)
        self.loop_checkbox = QCheckBox("Loop", self)
        self.step_forward_button = QPushButton(">>", self)
        self.step_backward_button = QPushButton("<<", self)
        self.frames_to_step = QLineEdit("10", self)
        self.visualization_mode = QComboBox(self)
        self.visualization_mode.addItems(["original", "grayscale", "difference"])

        # UI layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.loop_checkbox)
        layout.addWidget(self.step_forward_button)
        layout.addWidget(self.step_backward_button)
        layout.addWidget(self.frames_to_step)
        layout.addWidget(self.visualization_mode)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # UI connections
        self.open_button.clicked.connect(self.open_video)
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.loop_checkbox.stateChanged.connect(self.toggle_loop)
        self.step_forward_button.clicked.connect(self.step_forward)
        self.step_backward_button.clicked.connect(self.step_backward)
        self.visualization_mode.currentTextChanged.connect(self.update_frame)

        # Video capture
        self.video_capture = None
        self.prev_frame = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Video playback
        self.frame_time = 30  # Update frames every 30 ms
        self.loop = False

    def open_video(self):
        """Opens a video file."""
        video_file = QFileDialog.getOpenFileName(self, "Open Video", "C:\\", "Video Files (*.mp4)")

        if video_file is None:
            return

        logging.info("Loading video...")
        self.video_capture = cv2.VideoCapture(video_file[0])
        self.timer.start(self.frame_time)
        logging.info("Video loaded.")

    def read_frame(self):
        frame_read, frame = self.video_capture.read()
        if frame_read:
            return frame

        if self.loop:
            logging.debug("Looping video.")
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return self.read_frame()
        else:
            logging.debug("End of video.")
            self.timer.stop()
            return None

    def update_frame(self):
        """Updates the video frame."""
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        frame = self.read_frame()
        if frame is None:
            return
        frame_copy = frame.copy()

        logging.debug("Updating frame...")

        mode = self.visualization_mode.currentText()
        if mode == "original":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        elif mode == "grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        elif mode == "difference" and self.prev_frame is not None:
            frame = cv2.absdiff(frame, self.prev_frame)

        self.prev_frame = frame_copy  # Save the current frame for the next iteration

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                aspectRatioMode=Qt.KeepAspectRatio,
                transformMode=Qt.FastTransformation,
            )
        )

    def play_video(self):
        """Plays the video."""
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        logging.debug("Playing video...")
        self.timer.start(self.frame_time)

    def pause_video(self):
        """Pauses the video."""
        if not self.timer.isActive():
            return

        logging.debug("Pausing video...")
        self.timer.stop()

    def toggle_loop(self):
        """Toggles the loop state."""
        self.loop = not self.loop

    def step_forward(self):
        """Steps forward in the video. Stops at the end of the video."""
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        if self.timer.isActive():
            self.pause_video()

        try:
            step_size = int(self.frames_to_step.text())
        except ValueError:
            logging.error("Invalid step size.")
            return

        logging.debug("Stepping forward...")
        current_frame = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        target_frame = min(total_frames - 1, current_frame + step_size)

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        self.update_frame()

    def step_backward(self):
        """Steps backward in the video. Stops at the beginning of the video."""
        if self.video_capture is None or not self.video_capture.isOpened():
            return

        if self.timer.isActive():
            self.pause_video()

        try:
            step_size = int(self.frames_to_step.text())
        except ValueError:
            logging.error("Invalid step size.")
            return

        logging.debug("Stepping backward...")
        current_frame = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)
        target_frame = max(0, current_frame - step_size)

        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        self.update_frame()


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = VideoApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
