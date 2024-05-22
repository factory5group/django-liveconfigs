import datetime as dt
import logging

from django.core import exceptions
from django.core.management.base import BaseCommand

from liveconfigs.models import (DESCRIPTION_SUFFIX, TAGS_SUFFIX,
                                VALIDATORS_SUFFIX, BaseConfig, ConfigRow)

logger = logging.getLogger(__name__)


def save_row(instance_row, reset=False):
    logger.debug(f'save config row {instance_row.config_name}')
    try:
        db_row = ConfigRow.objects.get(name=instance_row.config_name)
        if reset or db_row.value is None:
            db_row.value = instance_row.last_value
            db_row.last_set = dt.datetime.now(tz=dt.timezone.utc)
        db_row.description = instance_row.description
        db_row.tags = instance_row.tags
        db_row.topic = instance_row.topic
        db_row.default_value = instance_row.default_value
        db_row.save()
    except exceptions.ObjectDoesNotExist:
        ConfigRow.objects.create(
            name=instance_row.config_name,
            value=instance_row.last_value,
            description=instance_row.description,
            tags=instance_row.tags,
            topic=instance_row.topic,
            last_set=dt.datetime.now(tz=dt.timezone.utc),
            default_value=instance_row.default_value,
        )


def load_config(reset=False, **kwargs):
    subclasses = set(BaseConfig.__subclasses__())
    for config in subclasses:
        for name, row in config.__dict__.items():
            if not any(
                [name.startswith('__'), name.endswith((DESCRIPTION_SUFFIX, TAGS_SUFFIX, VALIDATORS_SUFFIX))]
            ):
                save_row(row, reset=reset)
        logger.info(f"Config '{config.__name__}' load successfully")


class Command(BaseCommand):
    help = 'Загрузка дефолтных конфигов для админки (существующие параметры не перезаписываются)'

    def handle(self, *args, **kwargs):
        logger.info('Load started')
        load_config(**kwargs)
        logger.info('All configs load successfully')

    def add_arguments(self, parser):
        parser.add_argument(
            '-r',
            '--reset',
            action='store_true',
            default=False,
            help='Сбросить конфиги'
        )
