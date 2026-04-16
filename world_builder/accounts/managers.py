
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        return user

    def _create_user(self, email, username, password, **extra_fields):
        user = self._create_user_object(email, username, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    create_user.alters_data = True

    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, username, password, **extra_fields)

    create_superuser.alters_data = True


    # def create_user(self, email, username, password=None, **extra_fields):
    #     if not email:
    #         raise ValueError('Email is required')
    #     if not username:
    #         raise ValueError("The Username field must be set")
    #
    #     email = self.normalize_email(email)
    #     user = self.model(email=email, username=username, **extra_fields)
    #     user.set_password(password)
    #     user.save(using=self._db)
    #
    #     return user
    #
    # create_user.alters_data = True

    # def create_superuser(self, email, username, password=None, **extra_fields):
    #     extra_fields.setdefault("is_staff", True)
    #     extra_fields.setdefault("is_superuser", True)
    #     extra_fields.setdefault("is_active", True)
    #
    #     if extra_fields.get('is_staff') is not True:
    #         raise ValueError('Superuser must have is_staff=True.')
    #     if extra_fields.get('is_superuser') is not True:
    #         raise ValueError('Superuser must have is_superuser=True.')
    #
    #     return self.create_user(email, username, password, **extra_fields)
    #
    # create_superuser.alters_data = True
