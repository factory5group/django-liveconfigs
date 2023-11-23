from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import reverse_field_path
from django.core.exceptions import ValidationError
from django.db.models import Q
from more_admin_filters import MultiSelectFilter


class MultiSelectFilterByArrayField(MultiSelectFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__overlap' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        lookup_vals = request.GET.get(self.lookup_kwarg)
        self.lookup_vals = lookup_vals.split(',') if lookup_vals else list()
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.empty_value_display = model_admin.get_empty_value_display()
        parent_model, reverse_path = reverse_field_path(model, field_path)
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        lookup_choices = (queryset
                          .distinct()
                          .order_by(field.name)
                          .values_list(field.name))
        self.lookup_choices = {tag for config_row in lookup_choices if config_row[0] for tag in config_row[0]}
        super(admin.AllValuesFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.used_parameters = self.prepare_used_parameters(self.used_parameters)

    def queryset(self, request, queryset):
        params = Q()
        list_params = []
        lookup_arg = 'overlap'
        for lookup_arg, value in self.used_parameters.items():
            lookup_arg = lookup_arg
            list_params.append(value)
        if list_params:
            params = Q(**{lookup_arg: [param for params in list_params for param in params]})
        try:
            return queryset.filter(params)
        except (ValueError, ValidationError) as e:
            raise IncorrectLookupParameters(e)

    def prepare_used_parameters(self, used_parameters):
        for key, value in used_parameters.items():
            if not key.endswith('__overlap'):
                continue
            used_parameters[key] = value.split(',')
        return used_parameters
