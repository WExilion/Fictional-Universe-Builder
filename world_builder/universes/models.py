from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from common.models import NameModel
from common.validators import GenreNameValidator


# Create your models here.
class Universe(NameModel):
    genres = models.ManyToManyField(
        to='Genre',
        related_name='universes',
        blank=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        editable=False,
    )

    class Meta(NameModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_universe_name'
            ),
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_universe_slug'
            )
        ]


    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)

        if not self.pk:
            self.slug = base_slug
        else:
            old_instance = Universe.objects.get(pk=self.pk)
            if old_instance.name != self.name:
                self.slug = base_slug

        super().save(*args, **kwargs)



class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(limit_value=3, message='Genre must be at least 3 characters long.'),
            GenreNameValidator
        ]
    )


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
