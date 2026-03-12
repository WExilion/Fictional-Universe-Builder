from django.db import models

from common.models import BaseModel


# Create your models here.
class Character(BaseModel):
    role = models.CharField(
        max_length=50,
        blank=True
    )

    universe = models.ForeignKey(
        to='universes.Universe',
        on_delete=models.CASCADE,
        related_name='characters'
    )

    locations = models.ManyToManyField(
        to="locations.Location",
        related_name="characters"
    )
