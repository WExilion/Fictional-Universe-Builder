from django.db import models
from django.utils.text import slugify

from locations.choices import LocationType
from common.models import NameModel


# Create your models here.
class Location(NameModel):
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

    class Meta(NameModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'universe'],
                name='unique_name_per_universe',
                # violation_error_message="A location with this name already exists in this universe!"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.universe.slug}-{self.name}")
        super().save(*args, **kwargs)

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