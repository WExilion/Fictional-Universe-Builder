from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from accounts.choices import Gender
from accounts.managers import UserManager
from common.validators import NameValidator, FileSizeValidator, FileTypeValidator


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(
        unique=True
    )
    username = models.CharField(
        max_length=100,
        unique=True
    )

    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self) -> str:
        return self.username


class Profile(models.Model):
    owner = models.OneToOneField(
        to='User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[
            FileTypeValidator(),
            FileSizeValidator()
        ]
    )
    first_name = models.CharField(
        max_length=50,
        validators=[NameValidator],
        blank=True
    )
    last_name = models.CharField(
        max_length=50,
        validators=[NameValidator],
        blank=True
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    location = models.CharField(
        max_length=50,
        blank=True,
    )
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices, # noqa
        default=Gender.NONE,
        blank=True,
    )
    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Profile of {self.owner.username}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()