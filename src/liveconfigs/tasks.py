import logging

from liveconfigs.models.models import ConfigRow

logger = logging.getLogger(__name__)


def config_row_update_or_create(config_name: str, update_fields: dict):
    logger.info('save data to config %s', config_name)
    _, created = ConfigRow.objects.update_or_create(
        name=config_name, defaults=update_fields)
    return f"{config_name} was {'saved to DB' if created else 'updated in DB'}"
