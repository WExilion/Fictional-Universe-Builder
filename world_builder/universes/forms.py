from django import forms
from django.core.validators import MinLengthValidator

from common.mixins import NameLengthMixin, TimestampFormMixin
from common.validators import GenreNameValidator
from universes.models import Universe, Genre


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
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All Genres"
    )

class UniverseBaseForm(NameLengthMixin, forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        label="Select Genres",
        help_text="Pick up to 6 genres that best describe your universe. You can combine multiple.",
        widget = forms.CheckboxSelectMultiple(attrs={'class': 'genre-checkbox'})
    )
    new_genre = forms.CharField(
        max_length=50,
        required=False,
        help_text="Can't find your genre above? Add one here. Letters and hyphens only (e.g. Dark-Fantasy). Counts toward the 6 genre limit.",
        validators=[
            GenreNameValidator,
            MinLengthValidator(3, message="Genre must be at least 3 characters long.")
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Dark-Fantasy, Cyberpunk...',
            'class': 'form-control',
        })
    )


    class Meta:
        model = Universe
        # exclude = ['slug']
        fields = ['name', 'image_url', 'description', 'genres']
        labels = {
            'name': 'Universe Name',
            'image_url': 'Image URL',
            'description': 'Lore & Background',
        }
        help_texts = {
            'name': 'Enter a unique name for your fictional setting.',
            'image_url': 'Provide a direct link to an image (JPG, JPEG, PNG, GIF, WEBP, SVG).',
            'description': 'Provide a detailed background of your universe.',
        }

        error_messages = {
            'name': {
                'max_length': 'Whoa, that’s a mouthful. Let\'s keep the name under 100 characters.',
                'required': 'Please name your universe.'
            },
            'description': {
                'required': 'Your universe needs a backstory.',
            }
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., The Wizarding World, The Cosmere, Star Wars Galaxy...',
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'In a world where...',
                'class': 'form-control'
            }),
        }


    def clean_name(self):
        name = self._check_name_length(field_name='name', min_length=8, field_label='Universe Name')

        if Universe.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f"A universe named '{name}' already exists.")
        return name

    def clean_new_genre(self):
        new_genre = self.cleaned_data.get('new_genre')
        if new_genre:
            return new_genre.strip().title()
        return new_genre

    def clean(self):
        cleaned_data = super().clean()
        genres = cleaned_data.get('genres') or []
        new_genre = cleaned_data.get('new_genre')

        if new_genre:
            genre_names = [g.name.lower() for g in genres]

            if new_genre.lower() in genre_names:
                self.add_error(
                    'new_genre',
                    f'"{new_genre}" is already selected above — no need to add it again.'
                )
            if Genre.objects.filter(name__iexact=new_genre).exists():
                self.add_error(
                    'new_genre',
                    f'"{new_genre}" already exists in the genre list — select it from the checkboxes above.'
                )


        total = len(genres) + (1 if new_genre else 0)
        if total > 6:
            self.add_error(
                'genres',
                f'You selected {total} genres — please keep it to 6 or fewer in total.'
            )
        return cleaned_data


    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            self.save_m2m()

            new_genre_name = self.cleaned_data.get("new_genre")

            if new_genre_name:
                genre, _ = Genre.objects.get_or_create(name=new_genre_name)
                instance.genres.add(genre)

        return instance


class UniverseCreateForm(UniverseBaseForm):
    ...

class UniverseUpdateForm(TimestampFormMixin, UniverseBaseForm):
     class Meta(UniverseBaseForm.Meta):
         fields = UniverseBaseForm.Meta.fields


class UniverseDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        error_messages={
            'required': 'You must confirm before deleting.'
        }
    )

