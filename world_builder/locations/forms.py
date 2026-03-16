from django import forms
from django.db.models import Q
from django.utils.text import slugify

from common.mixins import NameLengthMixin
from locations.models import Location
from universes.models import Universe


class LocationBaseForm(NameLengthMixin, forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'image_url', 'type', 'description', 'universe', 'parent_location']
        labels = {
            'name': 'Location Name',
            'image_url': 'Image Link (Optional)',
            'type': 'Type (Optional)',
            'description': 'Description',
            'universe': 'Associated Universe',
            'parent_location': 'Located Within (Optional)',
        }

        help_texts = {
            'name': 'Enter a unique name for the location.',
            'image_url': 'Provide a direct link to an image file (JPG, JPEG, PNG, GIF, WEBP, SVG).',
            'tyoe': '',
            'description': 'Give some background details about your location.',
            'universe': 'You can select the associated universe.',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Hogwarts, Minas Tirith, Gotham City, The Shire, Winterfell...',
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/image.jpg',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'e.g., A high-tech metropolis powered by neon and steam...',
                'class': 'form-control',
                'rows': 6
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

        error_messages = {
            'name': {
                'max_length': 'That name is a bit too long. The limit is 100 characters.',
                'required': 'Please give your location a name.'
            },
            'description': {
                'required': 'Every location needs a backstory.',
            }
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
        return self._check_name_length(field_name='name', min_length=5, field_label='Location Name')


    def clean_parent_location(self):
        parent = self.cleaned_data.get("parent_location")

        if parent and parent.universe != self.cleaned_data.get("universe"):
            raise forms.ValidationError(
                "Parent location must belong to the same universe."
            )

        return parent

    def clean(self):
        cleaned_data = super().clean()
        name = self.cleaned_data.get('name')
        universe = self.cleaned_data.get('universe')

        if name and universe:
            generated_slug = slugify(f"{universe.slug}-{name}")

            duplicate = Location.objects.filter(
                Q(name__iexact=name) | Q(slug=generated_slug),
                universe=universe
            ).exclude(pk=self.instance.pk).first()

            if duplicate:
                if duplicate.name.lower() == name.lower():
                    self.add_error(
                        field='name',
                        error=f"A location named '{name}' already exists in {universe.name}."
                                   )
                else:
                    self.add_error(
                        field='name',
                        error=f"A location with a similar name to '{duplicate.name}' already exists in {universe.name}. "
                        f"Names like 'Planet Second' and 'Planet-Second', or 'O'reen' and 'Oreen' are considered the same."
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
                'Universe cannot be changed while a parent location is assigned. '
                'Remove the parent location and update first to change the universe.'
            )
        else:
            self.fields['universe'].help_text = 'No parent location assigned. You can change the universe.'




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
            'placeholder': 'Search location...',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )

    universe = forms.ModelChoiceField(
        queryset=Universe.objects.all(),
        required=False,
        empty_label="All Universe"
    )