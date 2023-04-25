import psycopg2
import logging
from config import URL

LOG = logging.getLogger(__name__)


class PostgreSQL:
    """Класс для подключение к PostgreSQL"""

    def __init__(self, url):
        try:
            self.connection = psycopg2.connect(url)
            self.connection.autocommit = True

            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT version();"
                )
                LOG.debug(
                    f'Server version: {cursor.fetchone()}'
                    '\nConnection successful')

        except Exception as exc:
            LOG.error(exc)

    def close_connection(self):
        """Закрытие подключения к базе данных"""

        if self.connection:
            self.connection.close()
            LOG.debug('Connection closed')

    def all_user_info(self, user_name):
        """Получение данных о пользователе (Все)"""

        users_dict = {
            'name': '',
            'rights': '',
            'login': '',
            'password': '',
            'time': '',
            'path': ''}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM users_data WHERE user_login = '{user_name}';")

                return dict(zip(users_dict, cursor.fetchone()[1:]))

        except Exception:
            return dict()

    def get_user_info(self, user_name):
        """Получение данных о пользователе (Имя, права, время работы)"""

        users_dict = {
            'name': '',
            'rights': '',
            'time': ''}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT user_name, user_rights, work_time FROM users_data WHERE user_name = '{user_name}';")

                result = dict(zip(users_dict, cursor.fetchone()))

            return f'Имя: {result.get("name", "")};\n' \
                   f'Права: {result.get("rights", "")};\n' \
                   f'Время работы за месяц: {result.get("time", "")} ч.'

        except Exception:
            return 'Нет такого пользователя'

    def _new_table(self):
        """Создание новой таблицы (При релизе метод будет удален)"""

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS users_data(
                    id serial primary key,
                    user_name varchar(50),
                    user_rights varchar(50),
                    user_login varchar(50),
                    user_password varchar(50),
                    work_time varchar(50),
                    path_to_photo varchar(100))'''
            )

            LOG.debug('Database created')

    def _delete_table(self):
        """Удаление таблицы (При релизе метод будет удален)"""

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''DROP TABLE users_data;''')

            LOG.debug('Database deleted')

    def _insert_info(self, user_name, user_rights, user_login, user_passwd, work_time, path_to_photo):
        """Добавление пользователя в базу данных (При релизе метод будет удален)"""

        with self.connection.cursor() as cursor:
            cursor.execute(
                f'''INSERT INTO users_data (
                user_name, user_rights, user_login, user_password, work_time, path_to_photo) VALUES (
                '{user_name}', '{user_rights}', '{user_login}',
                '{user_passwd}','{work_time}', '{path_to_photo}')'''
            )

        LOG.debug('info inserted')


if __name__ == '__main__':
    db = PostgreSQL(URL)
    db.close_connection()
