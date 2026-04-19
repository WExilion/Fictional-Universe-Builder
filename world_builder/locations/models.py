from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from common.mixins import SlugMixin
from locations.choices import LocationType
from common.models import NameModel

UserModel = get_user_model()

# Create your models here.
class Location(SlugMixin, NameModel):
    slug_source_field = 'name'

    type = models.CharField(
        max_length=50,
        choices=LocationType.choices, # noqa
    )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='locations'
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

    @property
    def full_path(self):
        if not hasattr(self, '_full_path_cache'):
            parts = [self.name]
            parent = self.parent_location

            while parent:
                parts.append(parent.name)
                parent = parent.parent_location

            self._full_path_cache = ', '.join(reversed(parts))

        return self._full_path_cache


    def get_absolute_url(self):
        return reverse('locations:detail', kwargs={
            'universe_slug': self.universe.slug,
            'slug': self.slug,
        })


    def get_descendant_pks(self):
        locations_pks = []
        queue = list(self.sub_locations.values_list('pk', flat=True))
        while queue:
            locations_pks.extend(queue)
            queue = list(self.__class__.objects.filter(parent_location__in=queue).values_list('pk', flat=True))
        return locations_pks
