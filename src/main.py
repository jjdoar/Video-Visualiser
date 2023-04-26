import logging
import sys

from app import VideoVisualizerApp
from visualization_mode import Original, Grayscale, Difference

from PyQt5.QtWidgets import QApplication


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = VideoVisualizerApp([Original(), Grayscale(), Difference()])
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
