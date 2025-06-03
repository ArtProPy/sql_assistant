import pytest

from tests.conftest import id_func
from tests.test_api.helper import read_test_data_from_yaml
from tests.test_api.test_models import User

test_data = read_test_data_from_yaml('tests/scrub/sql_assistant.yaml')


@pytest.mark.usefixtures('_clean_database')
@pytest.mark.parametrize('data', test_data['test_get_obj'], ids=id_func)
async def test_get_obj(data, create_users, sas):  # noqa: ARG001
    """
    Проверка получения объекта по id.

    :param data: тестовые данные
    :param client: тестовый клиент пользователя
    """

    # Перебор данных для запросов
    user = data.get('user', {})
    result = data.get('result')

    obj = await sas.get_obj(User, user.get('id'), error=False)

    if not result:
        assert obj is None, 'найден объект, которого не ждали'

        return

    assert obj is not None, 'объект не был найден'

    for key, value in result.items():
        assert (
            getattr(obj, key) == value
        ), f'`{key}` объекта не соответствует ожидаемому `{value}`'
