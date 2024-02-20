import json
from decimal import Decimal
from django import forms
from django.conf import settings
from liveconfigs.models import ConfigRow


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=2, sort_keys=True, **kwargs)


class ConfigRowForm(forms.ModelForm):
    class Meta:
        model = ConfigRow
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.LC_ENABLE_PRETTY_INPUT:
            max_len = settings.LC_MAX_STR_LENGTH_DISPLAYED_AS_TEXTINPUT or 50
            val = self.instance.value
            if isinstance(val, bool):
                self.fields["value"] = forms.BooleanField(
                    required=False,
                )
            elif isinstance(val, int):
                self.fields["value"] = forms.IntegerField(
                    required=False,
                )
            elif isinstance(val, float):
                self.fields["value"] = forms.FloatField(
                    required=False,
                    widget=forms.NumberInput(attrs={"step": "0.1"}),
                )
            elif isinstance(val, Decimal):
                self.fields["value"] = forms.DecimalField(
                    required=False,
                )
            elif isinstance(val, str):
                if len(val) <= max_len:
                    self.fields["value"] = forms.CharField(
                        required=False, widget=forms.TextInput({"size": max_len})
                    )
