from django import forms

from characters.models import Character
from common.mixins import NameLengthMixin
from locations.models import Location
from universes.models import Universe


class CharacterBaseForm(NameLengthMixin, forms.ModelForm):
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
        help_texts = {
            'first_name': 'The given name of your character.',
            'last_name': 'Family name, title, or house name.',
            'image_url': 'Direct link to a portrait or concept art (JPG, JPEG, PNG, GIF, WEBP, SVG).',
            'role': 'Define their place in the world.',
            'description': 'Describe their personality, appearance, or history.',
            'universe': 'Select the world this character belongs to.',
            'location': 'Where is this character currently residing?',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'e.g., Frodo, Katniss, Bruce',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'e.g., Baggins, Everdeen, Wayne',
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'class': 'form-control'
            }),
            'role': forms.TextInput(attrs={
                'placeholder': 'e.g., Protagonist, Villain, Merchant, or Guardian.',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Born in the heart of...',
                'class': 'form-control'
            }),
            'universe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        error_messages = {
            'first_name': {
                'required': 'Your character needs at least a first name.',
                'max_length': 'That first name is a bit too long (max 100 characters).',
            },
            'last_name': {
                'required': '',
                'max_length': 'Keep the last name under 100 characters.',
            },
            'role': {
                'max_length': 'Keep the role title brief (max 100 characters).',
            },
            'description': {
                'required': 'Tell us a bit about who this character is.',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['location'].queryset = Location.objects.filter(
                universe=self.instance.universe
            )

        elif 'universe' in self.data:
            self.fields['location'].queryset = Location.objects.filter(
                universe_id=self.data.get('universe')
            )

        else:
            self.fields['location'].queryset = Location.objects.none()

    def clean_first_name(self):
        return self._check_name_length(field_name='first_name', min_length=2)

    def clean_last_name(self):
        return self._check_name_length(field_name='last_name', min_length=2)


    def clean_location(self):
        universe = self.cleaned_data.get('universe')
        location = self.cleaned_data.get('location')

        if location and universe and location.universe != universe:
            raise forms.ValidationError(
                "Location must belong to the selected universe."
            )
        return location


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
                'Universe cannot be changed while a location is assigned. '
                'Remove the location and update first to change the universe.'
            )
        else:
            self.fields['universe'].help_text = 'No location assigned. You can change the universe.'


class CharacterDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
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
    universe = forms.ModelChoiceField(
        queryset=Universe.objects.all(),
        required=False,
        empty_label="All Universe"
    )