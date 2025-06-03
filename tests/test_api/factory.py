"""Создание тестовых данных."""

from random import choice, randint
from string import ascii_letters, digits

from tests.test_api.test_db import async_session
from tests.test_api.test_models import User


def rnd_int(start: int = 1_000, end: int = 1_000_000) -> int:
    """Генерация случайного числа."""

    return randint(start, end)


def rnd_str(start: int = 9, end: int = 15) -> str:
    """Генерация случайной строки."""

    return ''.join(
        choice(ascii_letters + digits) for _ in range(randint(start, end))
    )


async def make_user(
    _id=None,
    username=None,
    name=None,
    password=None,
    create_at=None,
    is_delete=False,
) -> User:
    """
    Создание пользователя для тестов.

    :param _id:
    :param username:
    :param name:
    :param password:
    :param create_at:
    :param is_delete:
    :return:
    """

    async with async_session() as session:
        # Генерация данных
        _id = _id if _id else rnd_int()
        username = username if username else rnd_str()
        name = name if name else rnd_str()
        password = password if password else rnd_str()
        # Создание пользователя
        user = User(
            id=_id,
            username=username,
            name=name,
            password=password,
            create_at=create_at,
            is_delete=is_delete,
        )
        session.add_all([user])
        # Сохранение изменений
        await session.commit()
        # Обновление данных о пользователе
        await session.refresh(user)

        return user
