from django.db import models

from common.models import BaseModel


# Create your models here.
class Location(BaseModel):
    class LocationType(models.TextChoices):
        COUNTRY = 'Country', 'Country'
        CITY = 'City', 'City'
        TOWN = 'Town', 'Town'
        WILDERNESS = 'Wilderness', 'Wilderness'
        DUNGEON = 'Dungeon', 'Dungeon'

    type = models.CharField(
        max_length=50,
        choices=LocationType.choices,
    )

    universe = models.ForeignKey(
        to='universes.Universe',
        on_delete=models.CASCADE,
        related_name='locations'
    )

    parent_location = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_locations',
    )

    def get_descendant_pks(self):
        pks = []
        for child in self.sub_locations.all():
            pks.append(child.pk)
            pks.extend(child.get_descendant_pks())
        return pks


    def get_full_path(self):
        parts = [self.name]
        parent = self.parent_location
        while parent is not None:
            parts.append(parent.name)
            parent = parent.parent_location
        return ', '.join(parts)