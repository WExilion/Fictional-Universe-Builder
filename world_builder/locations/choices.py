from django.db import models


class LocationType(models.TextChoices):
    COUNTRY = 'Country', 'Country'
    CITY = 'City', 'City'
    TOWN = 'Town', 'Town'
    WILDERNESS = 'Wilderness', 'Wilderness'
    DUNGEON = 'Dungeon', 'Dungeon'