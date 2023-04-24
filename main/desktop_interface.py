import sys
import os
import face_recognition
import cv2
from config import URL
from postgresdb import PostgreSQL
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QWidget, QMessageBox, QDesktopWidget

os.environ["QT_QPA_PLATFORM"] = "wayland"
face_cascade = cv2.CascadeClassifier(
    '/home/vmyakotin/PycharmProjects/pythonProject/cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    '/home/vmyakotin/PycharmProjects/pythonProject/cascades/haarcascade_eye.xml')


class FaceAuthenticationForm(QMainWindow):
    def __init__(self):
        super(FaceAuthenticationForm, self).__init__()

        self.setWindowTitle('Аутентификация')
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
            }
        """)

    def login(self):
        username = self.edit_username.text()
        password = self.edit_password.text()
        db = PostgreSQL(URL)
        user_info = db.get_info(username)

        if isinstance(user_info, dict) and username == user_info.get('login') and password == user_info.get('password'):

            self.centralWidget().deleteLater()
            self.video_player = VideoPlayer(user_info)

            self.hide()
            self.video_player.show()

        elif isinstance(user_info, dict) and username == user_info.get('login') and password != user_info.get('password'):
            QMessageBox.warning(self, "Ошибка", "Неправильный пароль")

        else:
            QMessageBox.warning(self, "Ошибка", "Нет пользователя с таким именем")


class VideoPlayer(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.setGeometry(200, 200, 600, 400)
        # Создаем виджет для отображения изображения
        self.image_label = QLabel(self)
        self.setCentralWidget(self.image_label)

        # Создаем таймер для обновления изображения
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

        # Создаем кнопки для авторизации
        self.start_auth_button = QPushButton("Start Authentication", self)
        self.start_auth_button.move(20, 420)
        self.start_auth_button.clicked.connect(self.start_authentication)

        self.back_button = QPushButton("Back", self)
        self.back_button.move(150, 420)
        self.back_button.clicked.connect(self.go_back)

        # Открываем видеопоток с веб-камеры
        self.cap = cv2.VideoCapture(0)

    def update_frame(self):
        # Захватываем кадр с веб-камеры
        ret, frame = self.cap.read()

        if ret:
            # Преобразуем кадр в изображение с использованием OpenCV
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Преобразуем кадр в черно-белый формат

            # Обнаруживаем лица на кадре
            faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.5, minNeighbors=5)

            # Рисуем прямоугольник вокруг лица
            for (x, y, w, h) in faces:
                roi_gray = frame_gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Обнаруживаем глаза на кадре
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.5, minNeighbors=5)

                # Рисуем прямоугольник вокруг глаз
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            # Отображаем изображение на экране
            height, width, channels = frame.shape
            qimage = QImage(frame, width, height, channels * width, QImage.Format_BGR888)

            # Создаем QPixmap из QImage для отображения в QLabel
            pixmap = QPixmap.fromImage(qimage)

            # Обновляем QLabel с новым изображением
            self.image_label.setPixmap(pixmap)

    # Создаем слот для обработки нажатия кнопки "Начать авторизацию"
    def start_authentication(self):
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

                        if face_distance[0] < 0.6:
                            QMessageBox.information(self, "Авторизация", "Вы успешно авторизовались")
                            return

                    QMessageBox.warning(self, "Авторизация", "Ошибка авторизации. Попробуйте еще раз")
                else:
                    QMessageBox.warning(self, "Ошибка", "Лица не обнаружены на кадре. Попробуйте еще раз")
            else:
                QMessageBox.warning(self, "Ошибка", "Лица не обнаружены на кадре. Попробуйте еще раз")

    # Создаем слот для обработки нажатия кнопки "Назад"
    def go_back(self):
        # Закрываем окно авторизации и возвращаемся к основному окну
        self.login_window = FaceAuthenticationForm()
        # Скрываем окно авторизации и отображаем окно с веб-камерой
        self.hide()
        self.login_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceAuthenticationForm()
    window.show()
    sys.exit(app.exec_())
