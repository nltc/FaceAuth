import sys
import logging
import os
from PyQt5.QtWidgets import QApplication
from desktop_interface import FaceAuthenticationForm

os.environ["QT_QPA_PLATFORM"] = "wayland"
os.environ["XDG_SESSION_TYPE"] = "x11"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    filename='logs.log', filemode='w')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceAuthenticationForm()
    window.show()
    sys.exit(app.exec_())
