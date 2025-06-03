"""Работа с БД."""

import contextlib
import sys

import loguru
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


class Storage:
    __log = None
    __base = None
    __async_session = None

    def __init__(self, base=None, async_session=None, log=None) -> None:
        """
        Инициализация класса.

        :param base: декларативная база
        :param async_session: генератор асинхронных сессий подключений к БД
        :param log: объект логирования
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
            self.log.error(msg)
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
    def log(self):
        return self.__log

    @property
    def base(self):
        return self.__base

    @property
    def async_session(self):
        return self.__async_session


class SqlAssistant(Storage):
    """Класс-помощник работы с БД."""
    # == Декораторы класса ==========================================================
    @staticmethod
    def check_session_param(func):
        """Декоратор проверки сессии."""

        async def wrapper(self, *args, session=None, **kwargs):
            """Проверка сессии и запуск логики."""
            # Попытка получить значение параметра session из kwargs
            if not isinstance(session, AsyncSession):
                # Генерация session
                async with self.async_session() as session:
                    result = await func(self, *args, session=session, **kwargs)
            else:
                # Использование переданного session
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

    # == Запросы в БД ===============================================================
    @check_session_param
    @check_error
    async def get_obj(self, db, id_: int, session=None):
        """
        Возвращает объект.

        :param id_: id объекта
        :param db: класс таблицы, из которой необходимо получить объект
        :param session: сессия работы с БД

        :raise Exception: программная ошибка

        :return: объект таблицы
        """

        try:
            obj = await session.get(db, id_)

            assert obj, f'Объект с id={id_} не найден!'

        except Exception as exp:
            msg = str(exp)
            self.log.error(msg)

            await session.rollback()
            raise exp

        else:
            return obj

    @check_session_param
    @check_error
    async def get_all_objs(  # noqa: C901, PLR0912
        self,
        db,
        where: list = [],
        order_by: list = [],
        group_by: list = [],
        join_lst: list = [],
        aggregate: dict = {},
        fields: list = [],
        session=None,
    ) -> list:
        """
        Возвращает все экземпляры переданного класса.

        :param db: класс таблицы из которой необходимо получить данные
        :param where: условия фильтрации
        :param order_by: параметры сортировки
        :param group_by: параметры группировки
        :param join_lst: список джойнов
        :param aggregate: словарь с агрегатными функциями
        :param fields: поля для выборки

        :return: список экземпляров
        """

        try:
            query = select(*fields) if fields else select(db)

            if join_lst:
                query = query.select_from(db)
                for data in join_lst:
                    if data.get('onclause'):
                        if data.get('type') == 'left':
                            query = query.outerjoin(data['target'],
                                                    data['onclause'])
                        else:
                            query = query.join(data['target'], data['onclause'])
                    elif data.get('type') == 'left':
                        query = query.outerjoin(data['target'])
                    else:
                        query = query.join(data['target'])

            if where:
                query = query.where(*where)

            if group_by:
                query = query.group_by(*group_by)

            if aggregate:
                for column, func in aggregate.items():
                    query = query.add_columns(
                        func(getattr(db, column)).label(column)
                    )

            if order_by:
                query = query.order_by(*order_by)

            objs = await session.execute(query)

            result = objs.unique().all() if fields else objs.unique().scalars().all()
        except Exception:
            await session.rollback()
            raise
        else:
            msg = f'Возвращён список значений таблицы `{db.__name__}` '
            if not fields:
                msg += f'{[x.id for x in result]}'
            self.log.debug(msg)
            return result
