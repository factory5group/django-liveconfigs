import json

from django.contrib import admin
from django.utils import timezone
from import_export import formats, resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from tablib import Dataset

from .filters import TagsListFilter
from .forms import ConfigRowForm
from .models import ConfigRow, HistoryEvent
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
    form = ConfigRowForm
    formats = [formats.base_formats.JSON]
    resource_class = ConfigRowResource
    list_display = ('name', 'value', 'is_changed', 'description', 'topic', 'tags', 'last_read', 'last_set')
    fields = ('name', 'value', 'default_value', 'is_changed', 'description', 'topic', 'tags', 'last_read', 'last_set')
    list_filter = ("topic", TagsListFilter,)
    readonly_fields = ('name', 'description', 'topic', 'tags', 'last_read', 'last_set', 'default_value', 'is_changed')
    search_fields = ('name', 'description', 'topic', 'tags')
    actions = ['set_selected_config_rows_to_default']

    def is_changed(self, obj):
        return '▢' if obj.value == obj.default_value else '☑'

    def save_model(self, request, obj, form, change):
        user = request.user
        super().save_model(request, obj, form, change)
        HistoryEvent.objects.create(name=obj.name, value=obj.value, edit_at=timezone.now(), edit_by=user)

    def set_selected_config_rows_to_default(self, request, queryset):
        user = request.user
        config_rows, history_events = [], []
        for config_row in queryset:
            config_row.value = config_row.default_value
            history_event = HistoryEvent(name=config_row.name, value=config_row.default_value,
                                         edit_at=timezone.now(), edit_by=user)
            config_rows.append(config_row)
            history_events.append(history_event)
        ConfigRow.objects.bulk_update(config_rows, ["value"])
        HistoryEvent.objects.bulk_create(history_events)


@admin.register(HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "edit_at", "edit_by")
    readonly_fields = list_display
    search_fields = ("name",)
    list_filter = ("name", "edit_at")


admin.site.register(ConfigRow, ConfigRowAdmin)
