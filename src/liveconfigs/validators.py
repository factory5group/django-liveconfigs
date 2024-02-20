def proper_name(f):
    def _named_generator(*args, **kwargs):
        new_f = f(*args, **kwargs)
        name = getattr(args[0], "__name__", args[0])
        new_f.__name__ = f'{f.__name__}_{"_".join(map(str, (name,) + args[1:]))}'
        return new_f

    return _named_generator


@proper_name
def equal_to(x):
    return lambda y: y == x


@proper_name
def greater_or_equal_than(x):
    return lambda y: y >= x


@proper_name
def greater_than(x):
    return lambda y: y > x


@proper_name
def less_or_equal_than(x):
    return lambda y: y <= x


@proper_name
def less_than(x):
    return lambda y: y < x


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


@proper_name
def dict_values_are(f: callable) -> callable:
    def _wrapper(x: dict) -> bool:
        return all(map(f, x.values()))

    return _wrapper
