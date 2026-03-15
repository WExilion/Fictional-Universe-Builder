from django.db import models


class LocationType(models.TextChoices):
    PLANET = 'Planet', "Planet"
    COUNTRY = 'Country', 'Country'
    CITY = 'City', 'City'
    TOWN = 'Town', 'Town'
    WILDERNESS = 'Wilderness', 'Wilderness'
    DUNGEON = 'Dungeon', 'Dungeon'