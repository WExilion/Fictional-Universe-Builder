from django.db import models
from django.utils.text import slugify

from common.validators import ImageURLValidator, NameValidator


# Create your models here.
class BaseModel(models.Model):
    image_url = models.URLField(
        blank=True,
        validators=[ImageURLValidator()]
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['-updated_at']

class NameModel(BaseModel):
    name = models.CharField(
        max_length=100,
        validators=[NameValidator()]
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        editable=False,
    )

    class Meta(BaseModel.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
