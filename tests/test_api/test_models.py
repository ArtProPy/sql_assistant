from sqlalchemy import Column, Integer, String, DateTime, func, Boolean

from tests.test_api.test_db import Base


class User(Base):
    """Таблица пользователей."""

    # Название таблицы
    __tablename__ = 'user'

    id = Column(Integer(), autoincrement=True, primary_key=True)  # noqa: A003
    username = Column(String(100), nullable=False, unique=True)
    name = Column(String(100))
    password = Column(String(100), nullable=False)
    create_at = Column(DateTime(), nullable=False, default=func.now())
    is_delete = Column(Boolean(), nullable=False, default=False)

    @property
    def print(self):  # noqa: A003
        """Выводит данные пользователя."""

        return f'{self.id} {self.username}'
