import datetime as dt
import json

from django.contrib import admin
from import_export import formats, resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from tablib import Dataset

from .filters import MultiSelectFilterByArrayField
from .models import ConfigRow
from .utils import get_excluded_rows


class ConfigRowResource(resources.ModelResource):
    value_ = Field(column_name='value')

    class Meta:
        model = ConfigRow
        import_id_fields = ('name',)
        fields = ('name', 'value')

    def dehydrate_value(self, cf):
        return cf.value

    def before_import_row(self, row, row_number=None, **kwargs):
        if 'value' in row:
            value = json.dumps(row['value'])
            row['value'] = value

    def import_data_inner(self, dataset: Dataset, dry_run, raise_errors,
                          using_transactions, collect_failed_rows, rollback_on_validation_errors=False, **kwargs):
        excluded_config_rows = get_excluded_rows()
        # dataset содержит все строки конфигов которые были описаны в импортирумом файле
        # в цикле мы удлаяем строки, которые не хотели бы импортировать и далее подменяем dataset
        for i, row_name in reversed(list(enumerate(dataset['name']))):
            if row_name in excluded_config_rows:
                del dataset[i]

        return super().import_data_inner(
            dataset, dry_run, raise_errors, using_transactions, collect_failed_rows,
            rollback_on_validation_errors=rollback_on_validation_errors, **kwargs
        )


class ConfigRowAdmin(ImportExportModelAdmin):
    formats = [formats.base_formats.JSON]
    resource_class = ConfigRowResource
    list_display = ('name', 'value', 'description', 'topic', 'tags', 'last_read', 'last_set')
    list_filter = ('topic', ('tags', MultiSelectFilterByArrayField),)
    readonly_fields = ('name', 'description', 'topic', 'tags', 'last_read', 'last_set')
    search_fields = ('name', 'description', 'topic', 'tags')

    def get_export_queryset(self, request):
        qs = ConfigRow.objects.all()
        excluded_config_rows = get_excluded_rows()
        return qs.exclude(name__in=excluded_config_rows)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.last_set = dt.datetime.now(tz=dt.timezone.utc)
        obj.save()


admin.site.register(ConfigRow, ConfigRowAdmin)
