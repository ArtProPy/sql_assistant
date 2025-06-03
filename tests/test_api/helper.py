"""Функции для помощи работы с тестами."""

from pathlib import Path

import yaml  # type: ignore[import-untyped]


def read_test_data_from_yaml(file_path):
    """Открытие yaml файла для полечение данных для тестов."""

    with Path.open(file_path, encoding='utf-8') as file:
        return yaml.safe_load(file)
