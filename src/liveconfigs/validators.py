def list_of_lists_includes_unique_elements(value):
    """Проверка на уникальность всех элементов внутри структуры типа [['str1', 'str2'], ['str3']]\n
    Внутри могут быть любые типы вместо строк

    Args:
        value: проверяемая структура

    Returns:
        True: Валидация пройдена успешно
        False: Валидация не пройдена
    """
    return len(sum(value, [])) == len(set(sum(value, [])))


def greater_than_x(x: int):
    """Проверка что значение конфига больше x
    Пример:\n
    DAYS_VALIDATORS = [validators.greater_than_x(0)]
    """
    def _func(value):
        return value > x
    setattr(_func, '__name__', f"greater_than_{x}")
    return _func
