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

![Экран редактирования конфига](https://github.com/factory5group/django-liveconfigs/blob/main/images/change_config.jpg?raw=true)


## Термины
+ __настройка__, __конфиг__ - одно типизированное именованное значение
+ __класс конфига__, __группа настроек__ - настройки, объединенные в один класс python
+ __топик__ - общая "тема" для группы настроек, по которой можно производить поиск настроек в админке.
У разных групп настроек в принципе может быть один и тот же топик
+ __теги__ - ключевые слова для быстрого поиска настроек. Одна настройка может иметь несколько тегов
## Со стороны разработчика

Для разработчика настройки выглядят как статические члены-константы классов python.
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

![Экран поиска и фильтрации конфигов](https://github.com/factory5group/django-liveconfigs/blob/main/images/filter_config.jpg?raw=true)

## Как начать пользоваться

1. Добавьте "liveconfigs" в INSTALLED_APPS в settings:
```
    INSTALLED_APPS = [
        ...,
        "liveconfigs",
    ]
```

2. Добавьте в settings еще несколько строк.
```
    # liveconfigs settings
    # Максимальная длина текста в значении конфига при которой отображать поле редактирования конфига как textinput
    # При длине текста в значении конфига большей этого значения - отображать поле редактирования конфига как textarea
    LC_MAX_STR_LENGTH_DISPLAYED_AS_TEXTINPUT = 50
    LC_ENABLE_PRETTY_INPUT = True
    LIVECONFIGS_SYNCWRITE = True    # sync write mode
    LC_CACHE_TTL = 1    # cache TTL in seconds (default = 1)
    # Максимальная длина значения конфига (в текстовом представлении) при которой значение в списке выводится целиком
    # При бОльшей длине визуал значения будет усечен ("Длинная строка" -> "Длин ... рока")
    LC_MAX_VISUAL_VALUE_LENGTH = 50
```

3. Заведите себе файл собственно с конфигами, например `config/config.py`
```python
from liveconfigs import models
from liveconfigs.validators import greater_than
from enum import Enum

# isort: off

# config_row_update_signal_handler begin
from django.conf import settings
from django.dispatch import receiver
from liveconfigs.signals import config_row_update_signal
from liveconfigs.tasks import config_row_update_or_create

# FIXME: Импорт приложения Celery из вашего проекта (если используете Celery)
# FIXME: Вам нужно изменить этот код, если вы используете не Celery
from celery_app import app

# isort: on

# Пример для Celery
# Реальное сохранение данных выполняет функция config_row_update_or_create
# Реализуйте отложенное сохранение удобным для вас методом
# Для Celery зарегистрируйте эту задачу в CELERY_TASK_ROUTES
# FIXME: Вам нужно изменить этот код, если вы используете не Celery
@app.task(max_retries=1, soft_time_limit=1200, time_limit=1500)
def config_row_update_or_create_proxy(config_name: str, update_fields: dict):
    config_row_update_or_create(config_name, update_fields)


@receiver(config_row_update_signal, dispatch_uid="config_row_update_signal")
def config_row_update_signal_handler(sender, config_name, update_fields, **kwargs):
    # Пример для Celery
    # При настройках для синхронного сохранения функция будет вызвана напрямую
    if settings.LIVECONFIGS_SYNCWRITE:
        config_row_update_or_create_proxy_func = config_row_update_or_create_proxy
    # При настройках для асинхронного сохранения функция будет вызвана через delay
    # FIXME: Вам нужно изменить этот код, если вы используете не Celery
    else:
        config_row_update_or_create_proxy_func = config_row_update_or_create_proxy.delay

    config_row_update_or_create_proxy_func(config_name, update_fields)


# config_row_update_signal_handler end


# тут перечислены возможные теги для настроек из вашей предметной области
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
    MY_FIRST_CONFIG_VALIDATORS = [greater_than(5)]
    
    # вторая настройка, без метаданных
    SECOND_ONE: bool = False  
```

4. Используете где-нибудь `FirstExample.MY_FIRST_CONFIG` как обычный int:
```python
from config.config import FirstExample
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
Чтобы запись последней даты чтения не тормозила вам всю систему (если,например, конфиги часто читаются разными частями кода),
можно вынести ее в задачу celery. Для этого:
 1. Установите переменную LIVECONFIGS_SYNCWRITE в `settings.py` в False:
 ```
     LIVECONFIGS_SYNCWRITE = False   # async write mode
 ```
 
 2. Если используете Celery, то настройте запуск задачи `config.config.config_row_update_or_create_proxy`:
 ```python
     CELERY_TASK_ROUTES = {
         'config.config.config_row_update_or_create_proxy': {
             'queue': 'quick', 'routing_key': 'quick'
         },
     }
 ```

 3. Если используете не Celery, то адаптируйте этот код под ваш случай

## Остались вопросы?
+ Посмотрите примеры использования конфигов: https://github.com/factory5group/django-liveconfigs-example/

+ Примеры использования валидаторов : https://github.com/factory5group/django-liveconfigs-example/

+ Примеры валидаторов : `validators.py` в https://github.com/factory5group/django-liveconfigs/

+ Напишите нам! 
