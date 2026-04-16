NAME_SORT_CHOICES = [
    ('name', 'A-Z'),
    ('-name', 'Z-A'),
    ('created', 'Oldest Created'),
    ('-created', 'Newest Created'),
    ('updated', 'Oldest Updated'),
    ('-updated', 'Newest Updated'),
]
FIRST_NAME_SORT_CHOICES = [
    ('first_name', 'A-Z'),
    ('-first_name', 'Z-A'),
    ('created', 'Oldest Created'),
    ('-created', 'Newest Created'),
    ('updated', 'Oldest Updated'),
    ('-updated', 'Newest Updated'),
]
TITLE_SORT_CHOICES = [
    ('title', 'A-Z'),
    ('-title', 'Z-A'),
    ('created', 'Oldest Created'),
    ('-created', 'Newest Created'),
    ('updated', 'Oldest Updated'),
    ('-updated', 'Newest Updated'),
]

SORT_OPTIONS = {
    'name': 'name',
    '-name': '-name',
    'first_name': 'first_name',
    '-first_name': '-first_name',
    'title': 'title',
    '-title': '-title',
    'created': 'created_at',
    '-created': '-created_at',
    'updated': 'updated_at',
    '-updated': '-updated_at',
}

