import sys
from PyQt5.QtWidgets import QApplication
from config import URL
from postgresdb import PostgreSQL
from desktop_interface import FaceAuthenticationForm
import logging
import os

os.environ["QT_QPA_PLATFORM"] = "wayland"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    filename='logs.log', filemode='w')


if __name__ == '__main__':
    db = PostgreSQL(URL)
    app = QApplication(sys.argv)
    window = FaceAuthenticationForm()
    window.show()
    db.close_connection()
    sys.exit(app.exec_())
