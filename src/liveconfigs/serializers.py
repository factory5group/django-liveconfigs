from rest_framework import serializers

from liveconfigs.models import ConfigRow


class ConfigRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigRow
        fields = ('name', 'value')

    def update_configs(self):
        for config in self.initial_data:
            config_row, _ = ConfigRow.objects.get_or_create(name=config['name'])
            config_row.value = config['value']
            config_row.save()
