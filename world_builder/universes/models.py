from django.core.validators import MinLengthValidator
from django.db import models

from common.models import BaseModel
from common.validators import NameValidator


# Create your models here.
class Universe(BaseModel):
    genres = models.ManyToManyField(
        to='Genre',
        related_name='universes',
        blank=True
    )
    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_universe_name')
        ]

class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3),
            NameValidator()
        ]
    )


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
