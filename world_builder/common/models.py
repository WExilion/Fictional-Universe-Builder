from django.db import models
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
        validators=[NameValidator]
    )

    class Meta(BaseModel.Meta):
        abstract = True

    def __str__(self):
        return self.name
