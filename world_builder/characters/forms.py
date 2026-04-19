from django import forms

from characters.models import Character
from common.choices import FIRST_NAME_SORT_CHOICES
from common.mixins import NameLengthMixin, OwnerScopedFormMixin
from locations.models import Location
from universes.models import Universe


class CharacterBaseForm(OwnerScopedFormMixin, NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Character
        fields = ['first_name', 'last_name', 'image_url', 'role', 'description', 'universe', 'location']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'image_url': 'Image Link (Optional)',
            'role': 'Role (Optional)',
            'description': 'Character Bio',
            'universe': 'Associated Universe',
            'location': 'Current Location (Optional)',

        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Frodo',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Baggins',
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
            }),
            'role': forms.TextInput(attrs={
                'placeholder': 'e.g. Hero, Merchant, or Villain.',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Tell us about your character...',
            }),
        }
        help_texts = {
            'first_name': 'Your character’s given name.',
            'last_name': 'Surname, house, or title.',
            'image_url': 'Link to a portrait. Supports JPG, PNG, or WEBP.',
            'role': 'Their job or social standing.',
            'description': 'Briefly detail their background and personality.',
            'universe': 'Choose the world they inhabit.'
        }
        error_messages = {
            'first_name': {
                'required': 'Enter a first name.',
                'max_length': 'First name must be 100 characters or fewer.',
            },
            'last_name': {
                'required': 'Enter a last name.',
                'max_length': 'Last name must be 100 characters or fewer.',
            },
            'role': {
                'max_length': 'Role title is too long (max 100 characters).',
            },
            'description': {
                'required': 'Enter a description for your character.',
            },
            'location': {
                'invalid_choice': 'Location must belong to the selected universe.'
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

        if universe_id:
            locations = Location.objects.filter(universe_id=universe_id)
            if owner_for_queryset is not None:
                locations = locations.filter(owner=owner_for_queryset)
            self.fields['location'].queryset = locations
        else:
            self.fields['location'].queryset = Location.objects.none()

    def clean_first_name(self):
        return self._check_name_length(field_name='first_name', min_length=2)

    def clean_last_name(self):
        return self._check_name_length(field_name='last_name', min_length=2)


class CharacterCreateForm(CharacterBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].disabled = True
        self.fields['location'].help_text = 'You can assign a location after creation.'

class CharacterUpdateForm(CharacterBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.location:
            self.fields['universe'].disabled = True
            self.fields['universe'].help_text = (
                'Universe is locked while a location is assigned. '
                'Clear the location field to enable changes.'
            )
        else:
            self.fields['universe'].help_text = 'Ensure the location is empty to switch universes.'
            self.fields['location'].help_text = (
                'Locations must inhabit the chosen universe. '
                'Empty this field before switching worlds.'
            )


class CharacterDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I confirm that I want to delete this character.",
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
            'placeholder': 'Search characters...',
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
        choices=FIRST_NAME_SORT_CHOICES,
        required=False,
        label='Sort By',
        widget=forms.Select(attrs={'class': 'form-select'})
    )