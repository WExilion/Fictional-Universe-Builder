from django import forms

from common.mixins import NameLengthMixin, TimestampFormMixin
from locations.models import Location


class LocationBaseForm(NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'image_url', 'description', 'type', 'universe', 'parent_location']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter location name',
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'Enter image URL',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter description',
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'universe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'parent_location': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'image_url': 'Image URL',
            'parent_location': 'Parent Location (optional)',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        if self.instance and self.instance.pk:
            universe = self.instance.universe
            excluded_pks = self.instance.get_descendant_pks()
            excluded_pks.append(self.instance.pk)

            self.fields['parent_location'].queryset = Location.objects.filter(
                universe=universe
            ).exclude(pk__in=excluded_pks)

        elif 'universe' in self.data:
            self.fields['parent_location'].queryset = Location.objects.filter(
                universe_id=self.data.get('universe')
            )

        else:
            self.fields['parent_location'].queryset = Location.objects.none()

    def clean_name(self):
        name = self._check_name_length(field_name='name', min_length=5, field_label='Location Name')

        universe = self.cleaned_data.get('universe')

        if universe and Location.objects.filter(
            name__iexact=name,
            universe=universe
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                f"A location named '{name}' already exists in this universe."
            )
        return name


    def clean_parent_location(self):
        parent = self.cleaned_data.get("parent_location")

        if parent and parent.universe != self.cleaned_data.get("universe"):
            raise forms.ValidationError(
                "Parent location must belong to the same universe."
            )

        return parent

class LocationCreateForm(LocationBaseForm):
    ...

class LocationUpdateForm(TimestampFormMixin, LocationBaseForm):
    class Meta(LocationBaseForm.Meta):
        fields = LocationBaseForm.Meta.fields

class LocationDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I want to delete this location",
        error_messages={
            'required': 'You must confirm before deleting.'
        }
    )

class SearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search universes...',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )
