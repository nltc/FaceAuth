import hashlib


def hash_password(password):
    """Хеширование пароля с использованием SHA-256"""

    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()


def check_password(password, hashed_password):
    """Проверка пароля"""

    return hashed_password == hash_password(password)


if __name__ == '__main__':
    pass
