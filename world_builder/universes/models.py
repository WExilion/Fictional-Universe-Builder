from django.core.validators import MinLengthValidator
from django.db import models

from common.models import NameModel
from common.validators import NameValidator


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
                # violation_error_message="A universe with this name already exists!"

            )
        ]

class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3, 'Genre name must be at least 3 characters long.'),
            NameValidator()
        ]
    )


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
