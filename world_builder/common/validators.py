import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class NameValidator:
    default_message = "Please use only letters, hyphens, spaces, or apostrophes. Numbers and symbols aren't allowed."
    def __init__(self, message: str = None) -> None:
        self.message = message or self.default_message

    def __call__(self, value: str) -> None:
        if not re.search(r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$", value):
            raise ValidationError(
                f"'{value}' is invalid. {self.message}"
            )


@deconstructible
class ImageURLValidator:
    def __init__(self, allowed_extensions: list[str] = None, message: str = None) -> None:
        self.allowed_extensions = allowed_extensions or ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
        self.pattern = rf'\.({"|".join(self.allowed_extensions)})(\?.*)?$'
        self.message = message or (
            f"The URL must point to a direct image ({', '.join(self.allowed_extensions)}). "
            "Tip: right-click an image and select 'Copy image address'."
        )

    def __call__(self, value: str) -> None:
        if not re.search(self.pattern, value, re.IGNORECASE):
            raise ValidationError(self.message)


# Maybe use it later to expand choice.
# @deconstructible
# class FileSizeValidator:
#     def __init__(self, file_size_mb: int, message: str = None) -> None:
#         self.file_size_mb = file_size_mb
#         self.message = message or f"The uploaded image exceeds the maximum allowed size of {self.file_size_mb} MB."
#
#     def __call__(self, value: UploadedFile) -> None:
#         if value.size > self.file_size_mb * 1024 * 1024:
#             raise ValidationError(self.message)