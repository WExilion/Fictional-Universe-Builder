from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse

from common.mixins import SlugMixin
from common.models import TimestampedModel
from common.validators import StoryTitleValidator

UserModel = get_user_model()

# Create your models here.
class Story(SlugMixin, TimestampedModel):
    slug_source_field = 'title'

    title = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(3),
            StoryTitleValidator
        ]
    )
    content = models.TextField()

    is_published = models.BooleanField(
        default=False
    )

    slug = models.SlugField(
        blank=True,
        editable = False,
    )

    owner = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='stories'
    )

    universe = models.ForeignKey(
        to='universes.Universe',
        on_delete=models.CASCADE,
        related_name='stories',
    )

    characters = models.ManyToManyField(
        to='characters.Character',
        related_name='stories',
        blank=True
    )

    class Meta(TimestampedModel.Meta):
        constraints = [
            # models.UniqueConstraint(
            #     fields=['title', 'universe'],
            #     name='unique_title_per_universe',
            # ),
            models.UniqueConstraint(
                fields=['slug', 'universe'],
                name='unique_story_slug_per_universe',
            )
        ]


    def get_absolute_url(self):
        return reverse('stories:detail', kwargs={
            'universe_slug': self.universe.slug,
            'slug': self.slug,
        })


    def __str__(self):
        return self.title





   # def save(self, *args, **kwargs):
    #     base_slug = slugify(self.title)
    #
    #     if not self.pk:
    #         slug = base_slug
    #     else:
    #         # old_instance = type(self).objects.get(pk=self.pk) # for reusability
    #         old_instance = Story.objects.only('title', 'universe').get(pk=self.pk)
    #
    #         if old_instance.title != self.title or old_instance.universe != self.universe:
    #             slug = base_slug
    #         else:
    #             slug = self.slug or base_slug
    #
    #     final_slug = slug
    #     counter = 1
    #
    #     while Story.objects.filter(
    #             slug=final_slug,
    #             universe=self.universe
    #     ).exclude(pk=self.pk).exists():
    #         final_slug = f"{slug}-{counter}"
    #         counter += 1
    #
    #     self.slug = final_slug
    #
    #     super().save(*args, **kwargs)