from django import forms

from common.choices import NAME_SORT_CHOICES
from common.mixins import NameLengthMixin, OwnerScopedFormMixin
from locations.models import Location
from universes.models import Universe


class LocationBaseForm(OwnerScopedFormMixin, NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'image_url', 'type', 'description', 'universe', 'parent_location']
        labels = {
            'name': 'Location Name',
            'image_url': 'Image Link (Optional)',
            'type': 'Location Type',
            'description': 'Description',
            'universe': 'Associated Universe',
            'parent_location': 'Located Within (Optional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Minas Tirith or Gotham City'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe the atmosphere, history, or landmarks...',
                'rows': 5
            }),
        }
        help_texts = {
            'name': 'The unique name for this location.',
            'image_url': 'Link to an image. Supports JPG, PNG, or WEBP.',
            'type': 'Choose the category that fits best (e.g., City, Region).',
            'description': 'Briefly detail the background of this place.',
            'universe': 'Select the world where this location exists.',
        }
        error_messages = {
            'name': {
                'required': 'Enter a location name.',
                'max_length': 'Location names must be 100 characters or fewer.'
            },
            'type': {
                'required': 'Select a location type.'
            },
            'description': {
                'required': 'Every location needs a backstory.',
            },
            'universe': {
                'required': 'Choose an associated universe.'
            },
            'parent_location': {
                'invalid_choice': 'This location must inhabit the chosen universe.'
            }
        }



    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.style_form_fields()

        owner_for_queryset = self.get_owner_for_queryset()
        universe_id = self.get_selected_universe_id()

        if owner_for_queryset is not None:
            self.fields['universe'].queryset = Universe.objects.filter(owner=owner_for_queryset)
        else:
            self.fields['universe'].queryset = Universe.objects.none()

        excluded_pks = []
        if self.instance.pk:
            excluded_pks = self.instance.get_descendant_pks()
            excluded_pks.append(self.instance.pk)

        if universe_id:
            parent_locations = Location.objects.filter(universe_id=universe_id)
            if owner_for_queryset is not None:
                parent_locations = parent_locations.filter(owner=owner_for_queryset)
            if excluded_pks:
                parent_locations = parent_locations.exclude(pk__in=excluded_pks)
            self.fields['parent_location'].queryset = parent_locations
        else:
            self.fields['parent_location'].queryset = Location.objects.none()

    def clean_name(self):
        return self._check_name_length(field_name='name', min_length=5, field_label='Location Name')

    def clean(self):
        cleaned_data = super().clean()
        name = self.cleaned_data.get('name')
        universe = self.cleaned_data.get('universe')

        if name and universe:
            exists = Location.objects.filter(
                name__iexact=name,
                universe=universe
            ).exclude(pk=self.instance.pk).exists()

            if exists:
                self.add_error(
                    field='name',
                    error=f"A story with this named '{name}' already exists in {universe.name}." # noqa
                )
        return cleaned_data



class LocationCreateForm(LocationBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_location'].disabled = True
        self.fields['parent_location'].help_text = 'You can assign a parent location after creation.'


class LocationUpdateForm(LocationBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.parent_location:
            self.fields['universe'].disabled = True
            self.fields['universe'].help_text = (
                'Universe is locked while a parent location is assigned. '
                'Clear the parent location field to enable changes.'
            )
        else:
            self.fields['universe'].help_text = "Ensure the parent location is empty to switch universes."
            self.fields['parent_location'].help_text = (
                'Parent locations must inhabit the chosen universe. '
                'Empty this field before switching worlds.'
            )


class LocationDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'placeholder': 'Search location...',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )
    universe = forms.CharField(
        max_length=100,
        required=False,
        label='Universe',
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by universe...',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )
    sort = forms.ChoiceField(
        choices=NAME_SORT_CHOICES,
        required=False,
        label='Sort By',
        widget=forms.Select(attrs={'class': 'form-select'})
    )