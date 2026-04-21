import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'webp']

NameValidator = RegexValidator(
    regex=r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$",
    message="Name must contain only Latin letters. You can use a single space, hyphen, or apostrophe between words."
)

GenreNameValidator = RegexValidator(
    regex=r"^[a-zA-Z]+(?:[ -][a-zA-Z]+)*$",
    message="Genre name must consist of Latin letters, optionally separated by a single space or hyphen."
)


StoryTitleValidator = RegexValidator(
    regex=r"^[A-Za-z0-9][A-Za-z0-9 '\".,:;!?()\-]*$",
    message="Title must start with a Latin letter or number and may contain spaces and common punctuation."
)




@deconstructible
class ImageURLValidator:
    def __init__(self, allowed_extensions: list[str] = None, message: str = None) -> None:
        self.allowed_extensions = allowed_extensions or ALLOWED_IMAGE_TYPES
        self.pattern = rf'\.({"|".join(self.allowed_extensions)})$'
        # self.pattern = rf'\.({"|".join(self.allowed_extensions)})(\?.*)?$'
        self.message = message or (
            f"The URL must point to a direct image ({', '.join(self.allowed_extensions)}). "
            "Tip: Right-click the image and select 'Open image in new tab'. "
            "If the image loads alone, copy the URL from that tab's address bar"
        )

    def __call__(self, value: str) -> None:
        parsed = urlparse(value)
        if not re.search(self.pattern, parsed.path, re.IGNORECASE):
            raise ValidationError(self.message)


@deconstructible
class PillowImageValidator:
    def __init__(self, allowed_types: list[str] = None, message: str = None) -> None:
        self.allowed_types = {t.lower().lstrip(".").replace("jpg", "jpeg") for t in (allowed_types or ALLOWED_IMAGE_TYPES)}
        self.message = message or f"Unsupported or invalid image. Allowed: {', '.join(sorted(self.allowed_types))}."

    def __call__(self, value: UploadedFile) -> None:
        if not all(hasattr(value, attr) for attr in ("read", "seek", "tell")):
            return

        pos = value.tell()
        try:
            value.seek(0)
            with Image.open(value) as img:
                fmt = (img.format or "").lower()
                if fmt not in self.allowed_types:
                    raise ValidationError(
                        f"Unsupported image type '{fmt or 'unknown'}'. "
                        f"Allowed: {', '.join(sorted(self.allowed_types))}.")

                img.verify()

        except (UnidentifiedImageError, OSError):
            raise ValidationError(self.message)

        finally:
            value.seek(pos)

@deconstructible
class FileSizeValidator:
    def __init__(self, file_size_mb: int = 5, message: str = None) -> None:
        self.file_size_mb = file_size_mb
        self.message = message or f"The uploaded image exceeds the maximum allowed size of {self.file_size_mb} MB."

    def __call__(self, value: UploadedFile) -> None:
        size = getattr(value, "size", None)
        if size is None:
            return
        if size > self.file_size_mb * 1024 * 1024:
            raise ValidationError(self.message)




# MAGIC_BYTES = {
#     'jpg':  (0, b"\xff\xd8\xff"),
#     'jpeg': (0, b"\xff\xd8\xff"),
#     'png':  (0, b"\x89PNG"),
#     'webp': (8, b"WEBP"),
# }
# @deconstructible
# class FileTypeValidator:
#     def __init__(self, allowed_types: list[str] = None, message: str = None) -> None:
#         self.allowed_types = [t.lower().lstrip(".") for t in (allowed_types or ALLOWED_IMAGE_TYPES)]
#         self.message = message or f"Unsupported file type. Allowed: {', '.join(self.allowed_types)}."
#
#
#     def __call__(self, value) -> None:
#         if not hasattr(value, "read"):
#             return
#
#         pos = value.tell() if hasattr(value, "tell") else None
#         header = value.read(16)
#
#         if hasattr(value, "seek"):
#             value.seek(pos or 0)
#
#         for allowed in self.allowed_types:
#             offset, magic = MAGIC_BYTES.get(allowed, (0, None))
#             if magic and header[offset:offset + len(magic)] == magic:
#                 return
#
#         raise ValidationError(self.message)









