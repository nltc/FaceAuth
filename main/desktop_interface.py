import sys
import os
import face_recognition
import cv2
from config import URL
from postgresdb import PostgreSQL
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QWidget, QMessageBox, QDesktopWidget)

os.environ["QT_QPA_PLATFORM"] = "wayland"
FACE_CASCADE = cv2.CascadeClassifier(
    '/home/vmyakotin/PycharmProjects/pythonProject/cascades/haarcascade_frontalface_default.xml')
EYE_CASCADE = cv2.CascadeClassifier(
    '/home/vmyakotin/PycharmProjects/pythonProject/cascades/haarcascade_eye.xml')


class FaceAuthenticationForm(QMainWindow):
    """Окно авторизации по логину и паролю"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Авторизация по лицу')
        self.resize(600, 400)
        screen_size = QDesktopWidget().screenGeometry()
        x = (screen_size.width() - self.width()) / 2
        y = (screen_size.height() - self.height()) / 2
        self.move(int(x), int(y))

        self.label_username = QLabel('Username')
        self.edit_username = QLineEdit()
        self.label_password = QLabel('Password')
        self.edit_password = QLineEdit()
        self.button_login = QPushButton('Login')
        self.button_login.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.edit_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.edit_password)
        layout.addWidget(self.button_login)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #4CAF50;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QMainWindow {
                background-color: #f0f0f0;
            }""")

    def login(self):
        """Кнопка авторизации"""

        username = self.edit_username.text()
        password = self.edit_password.text()
        db = PostgreSQL(URL)
        user_info = db.all_user_info(username)
        login_and_pwd = (
            True
            if username == user_info.get('login', '') and password == user_info.get('password', '')
            else False)
        login_and_not_pwd = (
            True
            if username == user_info.get('login', '') and password != user_info.get('password', '')
            else False)

        if login_and_pwd:
            self.video_player = VideoPlayer(user_info)
            self.hide()
            self.video_player.show()

        elif login_and_not_pwd:
            QMessageBox.warning(self, "Ошибка", "Неправильный пароль")

        else:
            QMessageBox.warning(self, "Ошибка", "Нет пользователя с таким именем")


class VideoPlayer(QMainWindow):
    """Окно авторизации по лицу"""

    def __init__(self, user_info):
        super().__init__()

        self.setWindowTitle('Авторизация по лицу')
        self.user_info = user_info
        self.resize(600, 400)

        self.image_label = QLabel(self)
        self.setCentralWidget(self.image_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

        self.start_auth_button = QPushButton("Начать аутентификацию", self)
        self.start_auth_button.setFixedWidth(200)
        self.start_auth_button.move(150, 420)
        self.start_auth_button.clicked.connect(self.start_authentication)

        self.back_button = QPushButton("Назад", self)
        self.back_button.move(380, 420)
        self.back_button.clicked.connect(self.go_back)

        self.cap = cv2.VideoCapture(0)

        self.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                    }
                    QLineEdit {
                        font-size: 16px;
                        padding: 6px;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                    }
                    QPushButton {
                        font-size: 16px;
                        padding: 8px;
                        background-color: #4CAF50;
                        color: #fff;
                        border: none;
                        border-radius: 4px;
                    }
                    QMainWindow {
                        background-color: #f0f0f0;
                    }""")

    def update_frame(self):
        """Рисование прямоугольников вокруг лица и глаз"""

        ret, frame = self.cap.read()

        if ret:
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(frame_gray, scaleFactor=1.5, minNeighbors=5)

            for (x, y, w, h) in faces:
                roi_gray = frame_gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                eyes = EYE_CASCADE.detectMultiScale(roi_gray, scaleFactor=1.5, minNeighbors=5)

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            height, width, channels = frame.shape
            qimage = QImage(frame, width, height, channels * width, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimage)

            self.image_label.setPixmap(pixmap)

    def start_authentication(self):
        """Кнопка авторизации по лицу"""

        ret, frame = self.cap.read()

        if ret:
            face_locations = face_recognition.face_locations(frame)

            if len(face_locations) > 0:
                user_image = face_recognition.load_image_file(self.user_info.get('path'))
                user_face_encodings = face_recognition.face_encodings(user_image)

                if len(user_face_encodings) > 0:
                    user_face_encoding = user_face_encodings[0]
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

                    for face_encoding in face_encodings:
                        face_distance = face_recognition.face_distance([user_face_encoding], face_encoding)

                        if face_distance[0] < 0.6 and self.user_info.get('rights', '') == 'User':
                            self.time_viewer_user = TimeViewerUser(self.user_info.get('time', ''))
                            self.hide()
                            self.cap.release()
                            cv2.destroyAllWindows()
                            self.time_viewer_user.show()

                        elif face_distance[0] < 0.6 and self.user_info.get('rights', '') == 'Admin':
                            self.time_viewer_admin = TimeViewerAdmin()
                            self.hide()
                            self.cap.release()
                            cv2.destroyAllWindows()
                            self.time_viewer_admin.show()

                        else:
                            QMessageBox.warning(self, "Авторизация", "Ошибка авторизации. Попробуйте еще раз")
                else:
                    QMessageBox.warning(self, "Ошибка", "Лица не обнаружены на кадре. Попробуйте еще раз")
            else:
                QMessageBox.warning(self, "Ошибка", "Лица не обнаружены на кадре. Попробуйте еще раз")

    def go_back(self):
        """Возвращение в окно авторизации по логину и паролю"""

        self.login_window = FaceAuthenticationForm()
        self.cap.release()
        cv2.destroyAllWindows()
        self.hide()
        self.login_window.show()


class TimeViewerUser(QMainWindow):
    """Окно счетчика времени пользователя"""

    def __init__(self, time):
        super().__init__()
        self.setWindowTitle('Авторизация по лицу')
        self.resize(600, 400)
        screen_size = QDesktopWidget().screenGeometry()
        x = (screen_size.width() - self.width()) / 2
        y = (screen_size.height() - self.height()) / 2
        self.move(int(x), int(y))
        self.time = time
        self.label_username = QLabel(f'В этом месяце вы отработали {self.time} часов !')
        self.label_username.setAlignment(Qt.AlignCenter)
        self.back_button = QPushButton('Вернуться в главное меню')
        self.back_button.clicked.connect(self.back_to_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.back_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setStyleSheet("""
            QLabel {
                font-size: 20px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #4CAF50;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

    def back_to_menu(self):
        """Возвращение в окно авторизации по логину и паролю"""

        self.login_window = FaceAuthenticationForm()
        self.hide()
        self.login_window.show()


class TimeViewerAdmin(QMainWindow):
    """Окно счетчика времени админа"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Авторизация по лицу')
        self.resize(600, 400)

        self.name_text = QLabel('Введите имя пользователя, чтобы узнать, сколько он отработал')
        self.label_username = QLabel('Поле для ввода имени:')
        self.edit_username = QLineEdit()
        self.select_button = QPushButton('Показать')
        self.select_button.clicked.connect(self.show_user_time)
        self.back_button = QPushButton('Вернуться в главное меню')
        self.back_button.clicked.connect(self.back_to_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.name_text)
        layout.addWidget(self.label_username)
        layout.addWidget(self.edit_username)
        layout.addWidget(self.select_button)
        layout.addWidget(self.back_button)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.setStyleSheet("""
            QLabel {
                font-size: 20px;
            }
            QLineEdit {
                font-size: 16px;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #4CAF50;
                color: #fff;
                border: none;
                border-radius: 4px;
            }
            QMainWindow {
                background-color: #f0f0f0;
            }""")

    def back_to_menu(self):
        """Возвращение в окно авторизации по логину и паролю"""

        self.login_window = FaceAuthenticationForm()
        self.hide()
        self.login_window.show()

    def show_user_time(self):
        """Показ информации о пользователях"""

        username = self.edit_username.text()
        db = PostgreSQL(URL)
        user_info = db.get_user_info(username)
        self.name_text.setText(user_info)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceAuthenticationForm()
    window.show()
    sys.exit(app.exec_())
