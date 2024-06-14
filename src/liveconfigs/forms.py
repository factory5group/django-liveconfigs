import json
from types import UnionType
from django import forms
from django.conf import settings
from liveconfigs.models import ConfigRow


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)


class JSONField(forms.JSONField):
    empty_values = [None, "", ()]


class ConfigRowForm(forms.ModelForm):
    class Meta:
        model = ConfigRow
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance_type = self.instance.registered_row_types.get(self.instance.name)
        if settings.LC_ENABLE_PRETTY_INPUT and not isinstance(instance_type, UnionType):
            max_len = settings.LC_MAX_STR_LENGTH_DISPLAYED_AS_TEXTINPUT or 50
            val = self.instance.value
            if instance_type is bool:
                self.fields["value"] = forms.BooleanField(
                    required=False,
                )
            elif instance_type is int:
                self.fields["value"] = forms.IntegerField(
                    required=False,
                )
            elif instance_type is float:
                self.fields["value"] = forms.FloatField(
                    required=False,
                    widget=forms.NumberInput(attrs={"step": "0.1"}),
                )
            elif instance_type is str:
                if len(val) <= max_len:
                    self.fields["value"] = forms.CharField(
                        required=False, widget=forms.TextInput({"size": max_len})
                    )
            elif isinstance(val, (list, dict)):
                self.fields["value"] = JSONField(encoder=PrettyJSONEncoder)
