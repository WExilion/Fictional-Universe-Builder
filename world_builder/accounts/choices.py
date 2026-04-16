from django.db import models

class Gender(models.TextChoices):
    NONE = '', ''
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'
    OTHER = 'Other', 'Other'