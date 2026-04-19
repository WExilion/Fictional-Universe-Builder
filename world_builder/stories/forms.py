from django import forms

from characters.models import Character
from common.mixins import NameLengthMixin, OwnerScopedFormMixin
from common.choices import TITLE_SORT_CHOICES
from stories.models import Story
from universes.models import Universe


class StoryBaseForm(OwnerScopedFormMixin, NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'content', 'is_published', 'universe', 'characters']
        labels = {
            'title': 'Title',
            'content': 'Content',
            'is_published': 'Published',
            'universe': 'Associated Universe',
            'characters': 'Associated Characters (Optional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'The Chronicles of...'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Once upon a time...',
                'rows': 20
            }),
        }
        help_texts = {
            'title': 'Choose a unique title for your tale.',
            'content': 'Write the next chapter of your journey.',
            'is_published': 'Make this story visible to the community',
            'universe': 'Select the world where this story unfolds.',
            'characters': 'Tag the characters featured in this tale.',
        }
        error_messages = {
            'title': {
                'required': 'Your story needs a title.',
                'max_length': 'Keep titles under 120 characters.'
            },
            'content': {
                'required': 'The page is still blank—tell your story!'
            },
            'universe': {
                'required': 'Choose a universe for this story.'
            },
            'characters': {
                'invalid_choice': 'Chosen characters must inhabit the selected universe.'
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
            characters = Character.objects.filter(universe_id=universe_id)
            if owner_for_queryset is not None:
                characters = characters.filter(owner=owner_for_queryset)
            self.fields['characters'].queryset = characters
        else:
            self.fields['characters'].queryset = Character.objects.none()





    def clean_title(self):
        return self._check_name_length(field_name='title', min_length=5, field_label='Story title')

    def clean(self):
        cleaned_data = super().clean()
        title = self.cleaned_data.get('title')
        universe = self.cleaned_data.get('universe')
        characters = self.cleaned_data.get('characters')

        if title and universe:
            exists = Story.objects.filter(
                title__iexact=title,
                universe=universe
            ).exclude(pk=self.instance.pk).exists()

            if exists:
                self.add_error(
                    field='title',
                    error=f"A story with this title '{title}' already exists in {universe.name}." # noqa
                )

        if characters and universe:
            if characters.exclude(universe=universe).exists(): # noqa
                self.add_error(
                    field='characters',
                    error=f"Selected characters must belong to the selected universe."
                )
        return cleaned_data


class StoryCreateForm(StoryBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['characters'].disabled = True
        self.fields['characters'].help_text = 'You can assign characters after creation.'

class StoryUpdateForm(StoryBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.characters.exists():
            self.fields['universe'].disabled = True
            self.fields['universe'].help_text = (
                'Cannot change universe while characters are assigned. '
                'Remove them first to update this setting.'
            )
        else:
            self.fields['universe'].help_text = 'Choose the world where this story unfolds.'
            self.fields['characters'].help_text = (
                'Characters must inhabit the chosen universe. '
                'Clear this field before switching worlds.'
            )

class StoryDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I want to delete this story.",
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
            'placeholder': 'Search story...',
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
        choices=TITLE_SORT_CHOICES,
        required=False,
        label='Sort By',
        widget=forms.Select(attrs={'class': 'form-select'})
    )