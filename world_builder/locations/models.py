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

    slug = models.SlugField(
        unique=False,
        blank=True,
        editable=False,
    )


    class Meta(NameModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'universe'],
                name='unique_name_per_universe',
            ),
            models.UniqueConstraint(
                fields=['slug', 'universe'],
                name='unique_location_slug_per_universe',
            )
        ]


    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)

        if not self.pk:
            self.slug = base_slug
        else:
            old_instance = Location.objects.get(pk=self.pk)
            if (old_instance.name != self.name or
                    old_instance.universe != self.universe):
                self.slug = base_slug

        super().save(*args, **kwargs)



    def get_descendant_pks(self):
        locations_pks = []
        queue = list(self.sub_locations.values_list('pk', flat=True))
        while queue:
            locations_pks.extend(queue)
            queue = list(self.__class__.objects.filter(parent_location__in=queue).values_list('pk', flat=True))
        return locations_pks


    def get_full_path(self):
        parts = [self.name]
        parent = self.parent_location

        while parent is not None:
            parts.append(parent.name)
            parent = parent.parent_location
        return ', '.join(parts)