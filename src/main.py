import logging
import sys

from app import VideoVisualizerApp
from visualization_mode import Motion, Original, Grayscale, Difference, Motion

from PyQt5.QtWidgets import QApplication


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = VideoVisualizerApp([Original(), Grayscale(), Difference(), Motion()])
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
