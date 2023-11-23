from django.core.management.base import BaseCommand

from liveconfigs.models import ConfigRow
from liveconfigs.utils import get_actual_config_names


class Command(BaseCommand):
    help = 'Удалить конфиги, которые есть в БД, но нет в коде'

    def handle(self, *args, **kwargs):
        actual_configs = get_actual_config_names()
        unused_configs = ConfigRow.objects.exclude(name__in=actual_configs)

        if not unused_configs:
            print("Нет неиспользуемых конфигов")
            return

        names_to_delete = "\n".join([c.name for c in unused_configs])
        print(f"Будут удалены {len(unused_configs)} конфигов:")
        print(names_to_delete)

        ack = input("Вы точно хотите удалить конфиги из списка выше? (y/n)\n")
        if ack == "y":
            unused_configs.delete()
            print("Неиспользуемые конфиги удалены")
