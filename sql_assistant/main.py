"""Работа с БД."""

import contextlib
import sys

import loguru
from sqlalchemy.orm import declarative_base, sessionmaker


class SqlAssistant:
    """Класс-помощник работы с БД."""

    __log = None
    __base = None
    __async_session = None

    def __init__(self, base=None, async_session=None, log=None) -> None:
        """
        Инициализация класса.

        :param base: декларативная база
        :param async_session: генератор асинхронных сессий подключений к БД
        :param log:  логгер
        """

        self.validate(log=log, base=base, async_session=async_session)

    def validate(self, base, async_session, log):
        """Валидация переданных данных."""

        results = [
            self.log_validate(log),
            self.base_validate(base),
            self.async_session_validate(async_session),
        ]

        if not any(results):
            sys.exit(1)

        self.__log.success('Все данные успешно были переданы!')

    def log_validate(self, log):
        """Валидация подключения функции логов проекта."""

        if log is None:
            log = loguru.logger
            log.add(
                'file.log',
                rotation='10 MB',
                compression='zip',
                level='TRACE',
                format='{name:25}| {time} | {level:8} | {message}',
            )

            msg = (
                'Создан собственный `logger`, т.к. не был передан `logger` проекта!'
            )
            log.warning(msg)

        self.__log = log

        return True

    def base_validate(self, base):
        """Валидация БД."""

        is_base = isinstance(base, type(declarative_base()))

        if not is_base:
            msg = 'Не был передан `Base` проекта!'
            self.__log.error(msg)
        else:
            self.__base = base

        return is_base

    def async_session_validate(self, async_session):
        """Валидация сессии подключения к БД асинхронно."""

        is_async_session = isinstance(async_session, type(sessionmaker()))

        if not is_async_session:
            msg = 'Не был передан `async_session` проекта!'
            self.__log.error(msg)
        else:
            self.__async_session = async_session

        return is_async_session

    @property
    async def log(self):
        return self.__log

    @property
    async def base(self):
        return self.__base

    @property
    async def async_session(self):
        return self.__async_session()

    @staticmethod
    def check_session_param(func):
        """Декоратор проверки сессии."""

        async def wrapper(self, *args, session=None, **kwargs):
            """Проверка сессии и запуск логики."""
            # Попытка получить значение параметра session из kwargs или args
            if not session:
                async with self.__async_session() as session:
                    result = await func(self, *args, session=session, **kwargs)
            else:
                result = await func(self, *args, session=session, **kwargs)

            return result

        return wrapper

    @staticmethod
    def check_error(func):
        """Декоратор проверки возврата ошибок."""

        async def wrapper(self, *args, error=True, **kwargs):
            """Проверка возврата ошибок."""
            # Возвращать ли ошибку при её возникновении
            if error:
                result = await func(self, *args, **kwargs)
            else:
                result = None
                with contextlib.suppress(Exception):
                    result = await func(self, *args, **kwargs)

            return result

        return wrapper

    @check_session_param
    @check_error
    async def get_obj(self, id_: int, db, session=None):
        """
        Возвращает объект.

        :param id_: id объекта
        :param db: класс таблицы, из которой необходимо получить объект
        :param session: сессия работы с БД

        :raise Exeption: программная ошибка

        :return: объект таблицы
        """

        try:
            obj = await session.get(db, id_)

            assert obj, f'Объект с id={id_} не найден!'

        except Exception as exp:
            msg = str(exp)
            self.__log.error(msg)

            await session.rollback()
            raise exp

        else:
            return obj
