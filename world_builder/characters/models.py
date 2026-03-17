from django.db import models
from django.utils.text import slugify

from common.models import BaseModel
from common.validators import NameValidator


# Create your models here.
class Character(BaseModel):
    first_name = models.CharField(
        max_length=50,
        validators=[NameValidator]
    )
    last_name = models.CharField(
        max_length=50,
        validators=[NameValidator]
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

    slug = models.SlugField(
        unique=False,
        blank=True,
        editable=False,
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'universe'],
                name='unique_character_slug_per_universe',
            )
        ]

    def __str__(self):
        return self.full_name

    def generate_slug(self, base_slug):
        slug = base_slug
        counter = 1

        qs = Character.objects.filter(universe=self.universe).exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        base_slug = slugify(f"{self.first_name}-{self.last_name}")

        if not self.pk:
            self.slug = self.generate_slug(base_slug)
        else:
            old_instance = Character.objects.get(pk=self.pk)
            if (old_instance.first_name != self.first_name or
                    old_instance.last_name != self.last_name or
                    old_instance.universe != self.universe):
                self.slug = self.generate_slug(base_slug)

        # if not self.slug or not self.slug.startswith(target_base):
        #     self.slug = self.generate_slug(target_base)

        super().save(*args, **kwargs)


        # self.slug = self.generate_slug()
        # super().save(*args, **kwargs)

    # Names being allowed to duplicate.



    # def save(self, *args, **kwargs):
    #     base_slug = slugify(f"{self.first_name}-{self.last_name}")
    #
    #     slug = base_slug
    #     counter = 1
    #
    #     qs = Character.objects.filter(universe=self.universe).exclude(pk=self.pk)
    #
    #     while qs.filter(slug=slug).exists():
    #         slug = f"{base_slug}-{counter}"
    #         counter += 1
    #
    #     self.slug = slug
    #
    #     super().save(*args, **kwargs)



        # base_slug = slugify(f"{self.universe.slug}-{self.first_name}-{self.last_name}")
        #
        # if not self.slug or not self.slug.startswith(base_slug):
        #     slug = base_slug
        #     counter = 1
        #     while Character.objects.filter(slug=slug).exclude(pk=self.pk).exists():
        #         slug = f"{base_slug}-{counter}"
        #         counter += 1
        #     self.slug = slug
        #
        # super().save(*args, **kwargs)


        # base_slug = slugify(f"{self.universe.slug}-{self.first_name}-{self.last_name}")

        # if not self.slug or not self.slug.startswith(base_slug):
        #     counter = 1
        #
        #     # 3. Standard uniqueness check
        #     while Character.objects.filter(slug=base_slug).exclude(pk=self.pk).exists():
        #         new_slug = f"{base_slug}-{counter}"
        #         counter += 1
        #
        #     self.slug = new_slug
        #
        # super().save(*args, **kwargs)



        # if Character.objects.filter(slug=base_slug).exclude(pk=self.pk).exists():
        #     count = Character.objects.filter(slug__startswith=f"{base_slug}-").exclude(pk=self.pk).count()
        #     self.slug = f"{base_slug}-{count + 1}"
        # else:
        #     self.slug = base_slug
        #
        # super().save(*args, **kwargs)


    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         super().save(*args, **kwargs)
    #         self.slug = slugify(f"{self.universe}-{self.first_name}-{self.last_name}-{self.pk}")
    #         super().save(update_fields=['slug'])
    #     else:
    #         self.slug = slugify(f"{self.universe}-{self.first_name}-{self.last_name}-{self.pk}")
    #         super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         super().save(*args, **kwargs)
    #     self.slug = slugify(f"{self.pk}-{self.first_name}-{self.last_name}")
    #     super().save(update_fields=['slug'])
