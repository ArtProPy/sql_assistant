def get_primary_keys_values(instance) -> dict:
    """
    Получение списка ключевых полей и их значений из экземпляра модели.

    :param instance: экземпляр SQLAlchemy модели, для которого нужно получить ключевые поля

    :return dict: словарь с именами ключевых полей (primary key) и их значениями
    """

    key_fields = {}

    for column in instance.__table__.columns:
        if column.primary_key:  # Проверка, является ли столбец первичным ключом
            key_fields[column.name] = getattr(instance, column.name)

    return key_fields
