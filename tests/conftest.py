"""Фикстуры для использования в проекте."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest

from sql_assistant.main import SqlAssistant
from tests.test_api.factory import (
    make_user,
)
from tests.test_api.helper import read_test_data_from_yaml
from tests.test_api.test_db import engine, Base, async_session

base_data = read_test_data_from_yaml('tests/scrub/base_data.yaml')
mock_log = MagicMock()


# Функция для создания идентификаторов
def id_func(param):
    """Возвращает название теста из его данных."""

    return param.get('name')


@pytest.fixture()
async def _clean_database() -> AsyncGenerator:
    """Очищает БД и создаёт стандартные данные."""

    if not engine.url.database.endswith('_test'):
        print('Попытка запустить тесты на бд прода!')
        return

    async with engine.begin() as conn:
        # Очистка всех таблиц
        await conn.run_sync(Base.metadata.drop_all)
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)

    # Создание новой сессии для теста
    async with async_session() as session:
        yield

        await session.close()

    async with engine.begin() as conn:
        # Очистка всех таблиц
        await conn.run_sync(Base.metadata.drop_all)


async def create_objs(need_objs: list[str]):
    """
    Создание тестовых объектов.

    :param need_objs: список необходимых объектов
    :return:
    """

    tasks = []
    # Порядок создоваемых объектов
    order = ['users']
    # Функции для создания объектов
    funct = {
        'users': make_user
    }

    for type_obj in order:
        if type_obj in need_objs:
            for test_obj in base_data[type_obj]:
                tasks.append(
                    asyncio.create_task(
                        funct[type_obj](**test_obj),  # type: ignore[operator]
                    ),
                )
            await asyncio.gather(*tasks)
            tasks.clear()


@pytest.fixture(name='create_users')
async def _create_test_users() -> AsyncGenerator:
    """Создаёт тестовых пользователей."""

    await create_objs(['users'])
    yield  # noqa: PT022


@pytest.fixture(name='sas')
async def sql_assistant() -> SqlAssistant:
    """Возвращает тестовый объект помощника."""

    return SqlAssistant(base=Base, async_session=async_session, log=mock_log)
