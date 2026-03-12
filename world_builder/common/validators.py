import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class NameValidator:
    message = "Names must contain at least one letter."
    def __call__(self, value):
        if not re.search(r'[^\W\d_]', value):
            raise ValidationError(
                f"'{value}' is invalid. {self.message}"
            )


@deconstructible
class ImageURLValidator:
    def __init__(self, allowed_extensions=None, message=None):
        self.allowed_extensions = allowed_extensions or ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
        self.pattern = rf'\.({"|".join(self.allowed_extensions)})(\?.*)?$'
        self.message = message or (
            f"The URL must point to a direct image ({', '.join(self.allowed_extensions)}). "
            "Tip: right-click an image and select 'Copy image address'."
        )

    def __call__(self, value) -> None:
        if not re.search(self.pattern, value, re.IGNORECASE):
            raise ValidationError(self.message)

