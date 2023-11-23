from liveconfigs.models import BaseConfig


def get_excluded_rows() -> list[str]:
    subclasses = set(BaseConfig.__subclasses__())
    excluded_config_rows = []
    for config_cls in subclasses:
        if isinstance(config_cls.__exported__, list):
            for config_row_name in config_cls.__dict__:
                if not config_row_name.startswith('__') and config_row_name not in config_cls.__exported__:
                    excluded_config_rows.append(config_cls.__prefix__ + config_row_name)
    return excluded_config_rows


def get_actual_config_names() -> list[str]:
    subclasses = set(BaseConfig.__subclasses__())
    actual_configs = []

    for config_cls in subclasses:
        for config_row_name in config_cls.__dict__:
            if not config_row_name.startswith('__'):
                actual_configs.append(config_cls.__prefix__ + config_row_name)

    return actual_configs
