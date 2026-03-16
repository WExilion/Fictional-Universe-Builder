from django.db import models


class LocationType(models.TextChoices):
    CONTINENT = 'Continent', "Continent"
    COUNTRY = 'Country', 'Country'
    CITY = 'City', 'City'
    TOWN = 'Town', 'Town'
    WILDERNESS = 'Wilderness', 'Wilderness'