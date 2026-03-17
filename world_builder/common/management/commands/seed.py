from django.core.management.base import BaseCommand
from universes.models import Universe, Genre
from locations.models import Location
from characters.models import Character
from locations.choices import LocationType

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self._seed_genres()
        self._seed_universes()
        self._seed_locations()
        self._seed_characters()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def _seed_genres(self):
        genres = [
            'Action', 'Adventure', 'Comedy', 'Drama', 'Epic Fantasy',
            'Fantasy', 'Historical', 'Horror', 'Martial Arts', 'Mature',
            'Mecha', 'Mystery', 'Psychological', 'Romance', 'Sci-fi',
            'Slice of Life', 'Sports', 'Space Fantasy', 'Supernatural',
            'Tragedy', 'Wuxia', 'Xianxia', 'Xuanhuan',
        ]

        for genre_name in genres:
            Genre.objects.get_or_create(name=genre_name)

        self.stdout.write('Genres seeded.')

    def _seed_universes(self):
        universe1, _ = Universe.objects.update_or_create(
            name='A Song of Ice and Fire',
            defaults={
                'description': 'The story of A Song of Ice and Fire takes place in a fictional world, primarily on a '
                               'continent called Westeros but also on a large landmass to the east, known as Essos. ',
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/d/dc/A_Song_of_Ice_and_Fire_book_collection_box_set_cover.jpg',
            }
        )
        universe1.genres.set(
            Genre.objects.filter(name__in=['Fantasy', 'Historical', 'Psychological', 'Drama'])
        )

        universe2, _ = Universe.objects.update_or_create(
            name='Star Wars',
            defaults={
                'description': 'Star Wars is a multi-generational "space opera" set "a long time ago in a galaxy far, far away".'
                               'The primary story follows the Skywalker family as they navigate a galactic conflict between '
                               'the democratic Galactic Republic and the authoritarian Galactic Empire.',
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Star_wars2.svg/1920px-Star_wars2.svg.png',
            }
        )
        universe2.genres.set(
            Genre.objects.filter(name__in=['Epic Fantasy', 'Sci-fi', 'Space Fantasy'])
        )

        universe3, _ = Universe.objects.update_or_create(
            name='Dune',
            defaults={
                'description': 'The story follows Paul Atreides, a young nobleman whose family is given control of the desert planet Arrakis, '
                               'the only source of the most valuable substance in the universe: the spice melange.'
                               'Arrakis is a hostile environment home to massive sandworms and the Fremen, a resilient '
                               'indigenous people who have adapted to the scarcity of water.',
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/d/de/Dune-Frank_Herbert_%281965%29_First_edition.jpg',
            }
        )
        universe3.genres.set(
            Genre.objects.filter(name__in=['Epic Fantasy', 'Sci-fi', 'Space Fantasy', 'Drama'])
        )

        self.stdout.write('Universes seeded.')

    def _seed_locations(self):
        # A Song of Ice and Fire
        asoiaf = Universe.objects.get(name='A Song of Ice and Fire')
        westeros, _ = Location.objects.update_or_create(name='Westeros', universe=asoiaf, defaults={
            'type': LocationType.CONTINENT, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/e/e0/Westeros.png',
            'description': 'The main continent where the Seven Kingdoms are located.'
        })
        essos, _ = Location.objects.update_or_create(name='Essos', universe=asoiaf, defaults={
            'type': LocationType.CONTINENT, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/2/28/Essos.png',
            'description': 'The vast continent to the east of Westeros, home to the Free Cities.'
        })
        the_north, _ = Location.objects.update_or_create(name='The North', universe=asoiaf, parent_location=westeros, defaults={
            'type': LocationType.REGION, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/f/f3/The_North.png',
            'description': 'The largest and coldest region of the Seven Kingdoms.'
        })
        Location.objects.update_or_create(name='Winterfell', universe=asoiaf, parent_location=the_north, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/1/1f/801_Winterfell_Overview.png',
            'description': 'The ancestral home of House Stark.'
        })
        Location.objects.update_or_create(name='King\'s Landing', universe=asoiaf, parent_location=westeros, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/8/83/King%27s_Landing_HotD.png',
            'description': 'The capital city of the Seven Kingdoms.'
        })
        Location.objects.update_or_create(name='Meereen', universe=asoiaf, parent_location=essos, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/gameofthrones/images/8/89/Meereen.png',
            'description': 'The largest of the Slaver Cities on the coast of Slaver\'s Bay.'
        })

        # Star Wars
        sw = Universe.objects.get(name='Star Wars')
        tatooine, _ = Location.objects.update_or_create(name='Tatooine', universe=sw, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://upload.wikimedia.org/wikipedia/en/6/6d/Tatooine_%28fictional_desert_planet%29.jpg',
            'description': 'A desert planet in the Outer Rim Territories.'
        })
        coruscant, _ = Location.objects.update_or_create(name='Coruscant', universe=sw, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://static.wikia.nocookie.net/starwars/images/8/84/CoruscantGlobeE1.png',
            'description': 'A city-covered planet and the political heart of the galaxy.'
        })
        naboo, _ = Location.objects.update_or_create(name='Naboo', universe=sw, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://static.wikia.nocookie.net/starwars/images/f/f0/Naboo_planet.png',
            'description': 'A lush, green planet home to the Gungans and the Naboo people.'
        })
        Location.objects.update_or_create(name='Mos Eisley', universe=sw, parent_location=tatooine, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/starwars/images/f/fd/Mos_Eisley.png',
            'description': 'A bustling spaceport on Tatooine, famous for its cantina.'
        })
        Location.objects.update_or_create(name='Jedi Temple', universe=sw, parent_location=coruscant, defaults={
            'type': LocationType.BUILDING,
            'image_url': 'https://static.wikia.nocookie.net/starwars/images/9/9f/JediTemple_cloudysky.jpg',
            'description': 'The headquarters and training center of the Jedi Order.'
        })

        # Dune
        dune = Universe.objects.get(name='Dune')
        arrakis, _ = Location.objects.update_or_create(name='Arrakis', universe=dune, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://static.wikia.nocookie.net/dune/images/8/82/Analog-DuneWorld-SchoenherrArrakis.png',
            'description': 'A desert planet and the only source of the spice melange.'
        })
        caladan, _ = Location.objects.update_or_create(name='Caladan', universe=dune, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://static.wikia.nocookie.net/dune/images/2/2c/CaladanEmperorBattleForDune.jpeg',
            'description': 'The ancestral home planet of House Atreides.'
        })
        giedi_prime, _ = Location.objects.update_or_create(name='Giedi Prime', universe=dune, defaults={
            'type': LocationType.PLANET, 
            'image_url': 'https://static.wikia.nocookie.net/dune/images/c/cf/GiediPrimeEmperorBattleForDune.jpeg',
            'description': 'The industrial and dark home planet of House Harkonnen.'
        })
        Location.objects.update_or_create(name='Arrakeen', universe=dune, parent_location=arrakis, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/dune/images/0/00/Arrakeen_governor%27s_palace_a.k.a._the_Arrakeen_Residency_%28Dune%2C_2021%29.jpg',
            'description': 'The capital city of the planet Arrakis.'
        })
        Location.objects.update_or_create(name='Sietch Tabr', universe=dune, parent_location=arrakis, defaults={
            'type': LocationType.CITY, 
            'image_url': 'https://static.wikia.nocookie.net/dune/images/5/5f/Frank_Herbert%27s_Dune_Calender_1978_-_Sietch_Tabr_%28art_by_John_Schoenherr%29.jpg',
            'description': 'A major Fremen community hidden in the deep desert.'
        })

        self.stdout.write('Locations seeded.')

    def _seed_characters(self):
        # A Song of Ice and Fire
        asoiaf = Universe.objects.get(name='A Song of Ice and Fire')
        Character.objects.update_or_create(
            first_name='Eddard', last_name='Stark', universe=asoiaf,
            defaults={
                'role': 'Lord of Winterfell', 
                'location': Location.objects.get(name='Winterfell', universe=asoiaf), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/5/52/Ned_Stark-Sean_Bean.jpg',
                'description': 'The honorable Lord of Winterfell and Warden of the North.'
            }
        )
        Character.objects.update_or_create(
            first_name='Jon', last_name='Snow', universe=asoiaf,
            defaults={
                'role': 'Steward of the Night\'s Watch', 
                'location': Location.objects.get(name='Winterfell', universe=asoiaf), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/3/30/Jon_Snow_Season_8.png',
                'description': 'The bastard son of Ned Stark, serving at the Wall.'
            }
        )
        Character.objects.update_or_create(
            first_name='Daenerys', last_name='Targaryen', universe=asoiaf,
            defaults={
                'role': 'Queen', 
                'location': Location.objects.get(name='Meereen', universe=asoiaf), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/0/0d/Daenerys_Targaryen_with_Dragon-Emilia_Clarke.jpg',
                'description': 'The Mother of Dragons and exiled Targaryen princess.'
            }
        )
        Character.objects.update_or_create(
            first_name='Tyrion', last_name='Lannister', universe=asoiaf,
            defaults={
                'role': 'Hand of the King', 
                'location': Location.objects.get(name='King\'s Landing', universe=asoiaf), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/5/50/Tyrion_Lannister-Peter_Dinklage.jpg',
                'description': 'The witty and intelligent youngest son of Lord Tywin Lannister.'
            }
        )

        # Star Wars
        sw = Universe.objects.get(name='Star Wars')
        Character.objects.update_or_create(
            first_name='Luke', last_name='Skywalker', universe=sw,
            defaults={
                'role': 'Jedi Knight', 
                'location': Location.objects.get(name='Tatooine', universe=sw), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/6/67/Luke_Skywalker_-_Welcome_Banner_%28Cropped%29.jpg',
                'description': 'The young farm boy who became a legendary Jedi Master.'
            }
        )
        Character.objects.update_or_create(
            first_name='Leia', last_name='Organa', universe=sw,
            defaults={
                'role': 'Princess', 
                'location': Location.objects.get(name='Naboo', universe=sw), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/1/1b/Princess_Leia%27s_characteristic_hairstyle.jpg',
                'description': 'A leader of the Rebel Alliance and daughter of Anakin Skywalker.'
            }
        )
        Character.objects.update_or_create(
            first_name='Han', last_name='Solo', universe=sw,
            defaults={
                'role': 'Smuggler', 
                'location': Location.objects.get(name='Mos Eisley', universe=sw), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/c/c9/Han_Solo_with_Blaster.jpg',
                'description': 'The charming pilot of the Millennium Falcon.'
            }
        )
        Character.objects.update_or_create(
            first_name='Darth', last_name='Vader', universe=sw,
            defaults={
                'role': 'Sith Lord',
                'location': Location.objects.get(name='Coruscant', universe=sw),
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/9/9c/Darth_Vader_-_2007_Disney_Weekends.jpg',
                'description': 'The fearsome Sith apprentice of Emperor Palpatine.'
            }
        )

        # Dune
        dune = Universe.objects.get(name='Dune')
        Character.objects.update_or_create(
            first_name='Paul', last_name='Atreides', universe=dune,
            defaults={
                'role': 'Duke', 
                'location': Location.objects.get(name='Arrakeen', universe=dune), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/f/ff/Timoth%C3%A9e_Chalamet_as_Paul_Atreides_%28Dune_2021%29.jpg',
                'description': 'The young heir of House Atreides, prophesied as the Kwisatz Haderach.'
            }
        )
        Character.objects.update_or_create(
            first_name='Chani', last_name='Kynes', universe=dune,
            defaults={
                'role': 'Fremen Warrior', 
                'location': Location.objects.get(name='Sietch Tabr', universe=dune), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/1/16/Zendaya_as_Chani_%28Dune_2021%29.jpg',
                'description': 'A fierce Fremen warrior and the love of Paul Atreides.'
            }
        )
        Character.objects.update_or_create(
            first_name='Vladimir', last_name='Harkonnen', universe=dune,
            defaults={
                'role': 'Baron', 
                'location': Location.objects.get(name='Giedi Prime', universe=dune), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/2/2d/Baron_Harkonnen-John_Schoenherr-Illustrated_Dune_%281978%29.jpg',
                'description': 'The cruel and cunning Baron of House Harkonnen.'
            }
        )
        Character.objects.update_or_create(
            first_name='Lady', last_name='Jessica', universe=dune,
            defaults={
                'role': 'Bene Gesserit', 
                'location': Location.objects.get(name='Caladan', universe=dune), 
                'image_url': 'https://upload.wikimedia.org/wikipedia/en/b/b6/Lady_Jessica_-_Rebecca_Ferguson_%282021%29.png',
                'description': 'A Bene Gesserit sister and the mother of Paul Atreides.'
            }
        )

        self.stdout.write('Characters seeded.')
