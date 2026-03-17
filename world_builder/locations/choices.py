from django.db import models


class LocationType(models.TextChoices):
    PLANET = 'Planet', "Planet"
    CONTINENT = 'Continent', "Continent"
    COUNTRY = 'Country', 'Country'
    REGION = 'Region', 'Region'
    CITY = 'City', 'City'
    DISTRICT = 'District', 'District'
    BUILDING = 'Building', 'Building'
    WILDERNESS = 'Wilderness', 'Wilderness'
    OTHER = 'Other', 'Other'