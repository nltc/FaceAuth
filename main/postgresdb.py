import psycopg2
import logging
from config import URL

LOG = logging.getLogger(__name__)


class PostgreSQL:
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
        if self.connection:
            self.connection.close()
            LOG.debug('Connection closed')

    def get_info(self, user_name):
        users_dict = {
            'name': '',
            'rights': '',
            'login': '',
            'password': '',
            'path': ''}

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM users_data WHERE user_login = '{user_name}';")

                return dict(zip(users_dict, cursor.fetchone()[1:]))
        except Exception:
            return dict()

    def _new_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS users_data(
                    id serial primary key,
                    user_name varchar(50),
                    user_rights varchar(50),
                    user_login varchar(50),
                    user_password varchar(50),
                    path_to_photo varchar(100))'''
            )

            LOG.debug('Database created')

    def _delete_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''DROP TABLE users_data;'''
            )

            LOG.debug('Database deleted')

    def _insert_info(self, user_name, user_rights, user_login, user_passwd, path_to_photo):
        with self.connection.cursor() as cursor:
            cursor.execute(
                f'''INSERT INTO users_data (
                user_name, user_rights, user_login, user_password, path_to_photo) VALUES (
                '{user_name}', '{user_rights}', '{user_login}',
                '{user_passwd}','{path_to_photo}')'''
            )
        LOG.debug('info inserted')


if __name__ == '__main__':
    db = PostgreSQL(URL)
    print(db.get_info('nlt'))
    # db._delete_table()
    # db._new_table()
    db.close_connection()
