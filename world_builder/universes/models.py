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

    class Meta(NameModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_universe_name',
                # violation_error_message="A universe with this name already exists."

            ),
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_universe_slug',
                # violation_error_message="A universe with a similar name already exists in this universe."

            )
        ]

    # maybe make it imposible to change the name?
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
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
