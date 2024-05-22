import datetime as dt
import logging
import time

from django.conf import settings
from django.core import exceptions

from liveconfigs.models.models import ConfigRow
from liveconfigs.signals import config_row_update_signal

logger = logging.getLogger()

DESCRIPTION_SUFFIX = "_DESCRIPTION"
TAGS_SUFFIX = "_TAGS"
VALIDATORS_SUFFIX = "_VALIDATORS"


CACHE_TTL = getattr(settings, 'LC_CACHE_TTL', 1)


class ConfigRowDescriptor:
    """ Кеширующий дескриптор для работы с конфигами """

    def __init__(self, config_name, default_value, description=None, topic=None, tags=None):
        self.config_name = config_name
        self.default_value = default_value
        self.last_value = default_value
        self.next_check = None
        self.description = description
        self.tags = tags
        self.topic = topic

    def __get__(self, obj, klass=None):
        now = time.time()
        if not self.next_check or now > self.next_check:
            dt_now = dt.datetime.now(tz=dt.timezone.utc)
            try:
                logger.info('accessing db to grab config %s', self.config_name)
                db_row = ConfigRow.objects.get(name=self.config_name)
                update_fields = {}
                if db_row.description != self.description:
                    update_fields['description'] = self.description
                if db_row.tags != self.tags:
                    update_fields['tags'] = self.tags
                if db_row.topic != self.topic:
                    update_fields['topic'] = self.topic
                if db_row.last_read is None or (db_row.last_read < dt_now - dt.timedelta(days=1)):
                    update_fields['last_read'] = dt_now
                if db_row.default_value != self.default_value:
                    update_fields['default_value'] = self.default_value
                if update_fields:
                    config_row_update_signal.send(sender=None, config_name=self.config_name,
                                                  update_fields=update_fields)
                self.last_value = db_row.value
            except exceptions.ObjectDoesNotExist:
                logger.warning('no config %s in db, using default value %s',
                               self.config_name, self.default_value)
                self.last_value = self.default_value
                update_fields = {
                    "name": self.config_name,
                    "value": self.last_value,
                    "description": self.description,
                    "tags": self.tags,
                    "topic": self.topic,
                    "last_read": dt_now,
                    "last_set": dt_now,
                    "default_value": self.default_value,
                }
                config_row_update_signal.send(
                    sender=None, config_name=self.config_name, update_fields=update_fields)

        self.next_check = now + CACHE_TTL
        return self.last_value


class ConfigMeta(type):
    """ Метакласс для конфигов. Подменяет все атрибуты на десктипторы """

    def __new__(cls, name, bases, dct):
        prefix = dct.get('__prefix__', '')
        topic = dct.get('__topic__', name)
        exported = dct.get('__exported__', '__all__')
        if prefix and not prefix.endswith('_'):
            prefix += '_'

        dct['__prefix__'] = prefix
        dct['__topic__'] = topic
        dct['__exported__'] = exported

        validators = dict()
        config_row_types = dict()
        if "__annotations__" in dct:
            config_row_types = dct["__annotations__"]

        for n, v in dct.items():
            if (
                not n.startswith('__')
                and not n.endswith((DESCRIPTION_SUFFIX, TAGS_SUFFIX, VALIDATORS_SUFFIX))
            ):
                if prefix and n in config_row_types:
                    config_row_types[prefix + n] = config_row_types.pop(n)
                dct[n] = ConfigRowDescriptor(prefix + n, v,
                                             description=dct.get(
                                                 n + DESCRIPTION_SUFFIX),
                                             tags=dct.get(n + TAGS_SUFFIX),
                                             topic=topic)
                validators[n] = dct.get(n + VALIDATORS_SUFFIX)

        dct = {
            name: value
            for name, value in dct.items()
            if not name.endswith((DESCRIPTION_SUFFIX, TAGS_SUFFIX, VALIDATORS_SUFFIX))
        }

        ConfigRow.registered_row_types.update(config_row_types)
        ConfigRow.validators.update(validators)
        c = super().__new__(cls, name, bases, dct)
        return c


class BaseConfig(metaclass=ConfigMeta):
    """От этого класса можно наследовать конфиги.
    За значениями этих конфигов система будет обращаться к БД и фоллбечиться
    на значения атрибутов, указаные в самом классе"""
