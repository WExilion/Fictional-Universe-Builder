from django import forms

class NameLengthMixin:
    default_min_length = 2

    def _check_name_length(self, field_name: str, min_length: int = None, field_label: str = None):
        min_length = min_length or self.default_min_length
        name = self.cleaned_data.get(field_name)
        label = field_label or field_name.replace('_', ' ').title()

        if name and len(name) < min_length:
            raise forms.ValidationError(
                f"{label} must be at least {min_length} characters long."
            )

        return name


class TimestampFormMixin:
    created_at = forms.DateTimeField(
        label="Date Created (Read-only)",
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True})
    )
    updated_at = forms.DateTimeField(
        label="Last Updated (Read-only)",
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, 'instance') and self.instance.pk:
            if 'created_at' in self.fields and hasattr(self.instance, 'created_at'):
                self.fields['created_at'].initial = self.instance.created_at
            if 'updated_at' in self.fields and hasattr(self.instance, 'updated_at'):
                self.fields['updated_at'].initial = self.instance.updated_at

