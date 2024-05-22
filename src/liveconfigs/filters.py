from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _


class JSONFieldListFilter(SimpleListFilter):
    """An admin list filter for ArrayFields."""

    def lookups(self, request, model_admin):
        """Return the filtered queryset."""
        queryset_values = model_admin.model.objects.values_list(
            self.parameter_name, flat=True
        )
        values = []
        for sublist in queryset_values:
            if sublist:
                for value in sublist:
                    if value:
                        values.append((value, value))
            else:
                values.append(("null", "-"))
        return sorted(set(values))

    def get_lookup_next(self, filter_params: dict, lookup: str):
        parameter_name = self.parameter_name
        lookup_next: list | str | None = filter_params.get(parameter_name) or []
        if lookup_next:
            lookup_next = (
                lookup_next[0].split(",")
                if isinstance(lookup_next, list)
                else lookup_next.split(",")
            )
        if lookup in lookup_next:
            lookup_next.remove(lookup)
        else:
            lookup_next.append(lookup)
        return ",".join(lookup_next)

    def choices(self, changelist):
        add_facets = False
        try:
            add_facets = changelist.add_facets
            facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        except AttributeError:
            # в Django < 5.0 нет этого функционала
            pass
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }

        for i, (lookup, title) in enumerate(self.lookup_choices):
            if add_facets:
                if (count := facet_counts.get(f"{i}__c", -1)) != -1:
                    title = f"{title} ({count})"
                else:
                    title = f"{title} (-)"
            lookup_next = self.get_lookup_next(changelist.get_filters_params(), lookup)

            yield {
                "selected": str(lookup) in (self.value() or []),
                "query_string": (
                    changelist.get_query_string({self.parameter_name: lookup_next})
                    if lookup_next
                    else changelist.get_query_string(remove=[self.parameter_name])
                ),
                "display": title,
            }

    def value(self):
        """
        Return the value (in string format) provided in the request's
        query string for this filter, if any, or None if the value wasn't
        provided.
        """
        _value = self.used_parameters.get(self.parameter_name)
        if _value:
            _value = _value.split(",")
        return _value

    def queryset(self, request, queryset):
        """Return the filtered queryset."""
        lookup_value = self.value()
        if lookup_value:
            lookup_filter = (
                {"{}__isnull".format(self.parameter_name): True}
                if lookup_value == "null"
                else {"{}__has_any_keys".format(self.parameter_name): lookup_value}
            )
            queryset = queryset.filter(**lookup_filter)
        return queryset


class TagsListFilter(JSONFieldListFilter):
    title = "tags"
    parameter_name = "tags"
