from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse

from common.mixins import SlugMixin
from common.models import BaseModel
from common.validators import NameValidator

UserModel = get_user_model()

# Create your models here.
class Character(SlugMixin, BaseModel):
    slug_source_field = 'full_name'
    slug_dependency_fields = ("first_name", "last_name")

    first_name = models.CharField(
        max_length=50,
        validators=[
            NameValidator,
            MinLengthValidator(2)
        ]
    )
    last_name = models.CharField(
        max_length=50,
        validators=[
            NameValidator,
            MinLengthValidator(2)
        ]
    )

    role = models.CharField(
        max_length=50,
        blank=True
    )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='characters'
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

    slug = models.SlugField(
        blank=True,
        editable=False,
    )

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'universe'],
                name='unique_character_slug_per_universe',
            )
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_absolute_url(self):
        return reverse('characters:detail', kwargs={
            'universe_slug': self.universe.slug,
            'slug': self.slug,
        })

    def __str__(self):
        return self.full_name
