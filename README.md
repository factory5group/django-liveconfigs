# LiveConfigs

LiveConfigs помогает настраивать приложение "на лету" через django-админку без перевыкатки и перезапуска. 
Сама конфигурация хранится в БД, но для разработчика скрыта за удобным программным интерфейсом.

## Быстрый пример

Создаем настройки

```python
class MyConfig(liveconfigs.BaseConfig):
   IS_FEATURE_ENABLED: bool = False
   NEW_FEATURE_VALUE: float = 20.4
```

Используем их

```python
if MyConfig.IS_FEATURE_ENABLED:
   print('feature is enabled and feature value is', MyConfig.NEW_FEATURE_VALUE)
```

Меняем через админку!

![Экран редактирования конфига](/images/change_config.jpg)


## Термины
+ __настройка__, __конфиг__ - одно типизированное именованное значение
+ __класс конфига__, __группа настроек__ - настройки, объединенные в один класс python
+ __топик__ - общая "тема" для группы настроек, по которой можно производить поиск настроек в админке.
У разных групп настроек в принципе может быть один и тот же топик
+ __теги__ - ключевые слова для быстрого поиска настроек. Одна настройка может иметь несколько тегов
## Со стороны разработчика

Для разработчика настройки выглядят как статические члены-константы классов  python.
Их можно быстро добавить, убрать, их просто использовать (пара строк кода). Их понимает mytype и среды разработки.

За создание новых конфигов отвечает разработчик.
Значения по-умолчанию хранятся в коде.
В БД новые конфиги попадают при выкатке или при первом использовании.


## Со стороны администратора 
Значения задаются через админку django. 
Для удобного администрирования конфиги поддерживают
+ __теги__ и __топики__ для группировки и поиска
+ документацию
+ автоматическую загрузку новых конфигов в бд
+ валидацию при изменении (типы и значения)
+ сохранение даты последних изменений и чтений конфигов
+ импорт и экспорт (удобно для тестирования системы)

![Экран поиска и фильтрации конфигов](/images/filter_config.jpg)

## Как начать пользоваться

1. Добавьте "liveconfigs" в INSTALLED_APPS в settings:
```
    INSTALLED_APPS = [
        ...,
        "liveconfigs",
    ]
```

2. Добавьте в settings еще одну строку.
```
    LIVECONFIGS_SYNCWRITE = True    # sync write mode
```

3. Заведите себе файл собственно с конфигами, например `configs/configs.py`
```python
from liveconfigs import models
from liveconfigs.validators import greater_than_x
from enum import Enum
...

# тут перечислены возможные теги для настроек
# из вашей предметной области
class ConfigTags(str, Enum):
    front = "Настройки для фронта"
    features = "Фичи"
    basic = "Основные"
    other = "Прочее"

# тут описана сама настройка и ее мета-данные
class FirstExample(models.BaseConfig):
    __topic__ = 'Основные настройки'  # короткое описание группы настроек
    MY_FIRST_CONFIG: int = 40
    # следующие строчки необязательны
    MY_FIRST_CONFIG_DESCRIPTION = "Какая-то моя настройка"
    MY_FIRST_CONFIG_TAGS = [ConfigTags.basic, ConfigTags.other]
    MY_FIRST_CONFIG_VALIDATORS = [greater_than_x(5)]
    
    # вторая настройка, без метаданных
    SECOND_ONE: bool = False  
```

4. Используете где-нибудь `FirstExample.MY_FIRST_FLAG` как обычный int:
```python
from configs.configs import FirstExample
...
if FirstExample.MY_FIRST_CONFIG > 20:
    print("Hello there!")
```

## Просмотр и редактирование конфигов в админке django
Редактировать значения конфигов можно по адресу
 http://YOUR_HOST/admin/liveconfigs/configrow/

При установке значений проверяется тип нового значения, а также вызываются
дополнительные валидаторы

## Автоматическая загрузка новых конфигов в БД
При первом обращении к настройке приложение проверяет,
есть ли запись о них в БД. Если ее нет, то конфиг записывается
в БД со значением по-умолчанию.

Если по какой-то причине вы не хотите ждать, то залить все новые конфиги 
в БД можно и на старте сервиса, добавив
в ваш скрипт запуска вызов команды load_config:

```sh
    # какие-то старые команды
    python /app/manage.py migrate --noinput
    python /app/manage.py collectstatic --noinput

    #  НОВАЯ СТРОЧКА - загрузка конфигов в бд
    python /app/manage.py load_config

    #  сам запуск сервиса - может быть и так
    python /app/manage.py runserver_plus 0.0.0.0:8080 --insecure
```

## Даты последнего изменения и чтения
В БД у каждой настройки есть два дополнительных поля - даты последнего чтения
и записи. Они помогают определить в живой системе, нужны ли все еще какие-то настройки
или пора уже от них избавиться.
### Асинхронная запись
Чтобы запись последней даты чтения не тормозила вам всю систему (если,например, конфиги часто читаются разными частами кода),
можно вынести ее в задачу celery. Для этого:
 1. Установите переменную LIVECONFIGS_SYNCWRITE в `settings.py` в False:
 ```
     LIVECONFIGS_SYNCWRITE = False   # async write mode
 ```
 
 2. Настройте запуск задачи `liveconfigs.tasks.config_row_update_or_create`:
 ```python
     CELERY_TASK_ROUTES = {
         'liveconfigs.tasks.config_row_update_or_create': {
             'queue': 'quick', 'routing_key': 'quick'
         },
     }
 ```

## Остались вопросы?
Посмотрите примеры использования конфигов: https://gitlab.xplanet.tech/common/liveconfigs-example/

Примеры валидаторов : `validators.py` в https://gitlab.xplanet.tech/common/liveconfigs-example/
Напишите нам! 
