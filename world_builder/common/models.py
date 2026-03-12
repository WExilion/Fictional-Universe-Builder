from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.text import slugify

from common.validators import ImageURLValidator, NameValidator


# Create your models here.
class BaseModel(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(5),
            NameValidator()
        ]
    )

    img = models.URLField(
        blank=True,
        validators=[ImageURLValidator()]
    )

    description = models.TextField(
        validators=[
            MinLengthValidator(50),
            MaxLengthValidator(5000)
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.pk}")
            super().save(update_fields=['slug'])
        else:
            super().save(*args, **kwargs)

