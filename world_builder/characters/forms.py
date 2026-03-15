from django import forms

from characters.models import Character
from common.mixins import TimestampFormMixin, NameLengthMixin
from locations.models import Location


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

class CharacterBaseForm(NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Character
        fields = ['first_name', 'last_name', 'role', 'image_url', 'description', 'universe', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter first name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter last name',
                'class': 'form-control'
            }),
            'role': forms.TextInput(attrs={
                'placeholder': 'Enter role (optional)',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter description',
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'class': 'form-control'
            }),
            'universe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
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
    ...
class CharacterUpdateForm(TimestampFormMixin, CharacterBaseForm):
    class Meta(CharacterBaseForm.Meta):
        fields = CharacterBaseForm.Meta.fields



class CharacterDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I want to delete this character",
        error_messages={
            'required': 'You must confirm before deleting.'
        }
    )