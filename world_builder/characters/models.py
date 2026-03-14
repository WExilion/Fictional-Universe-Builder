from django.db import models

from common.models import BaseModel
from common.validators import NameValidator


# Create your models here.
class Character(BaseModel):
    first_name = models.CharField(
        max_length=50,
        validators=[NameValidator()]
    )
    last_name = models.CharField(
        max_length=50,
        validators=[NameValidator()]
    )

    role = models.CharField(
        max_length=50,
        blank=True
    )

    universe = models.ForeignKey(
        to='universes.Universe',
        on_delete=models.CASCADE,
        related_name='characters'
    )

    location = models.ForeignKey(
        to='locations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters'
    )
