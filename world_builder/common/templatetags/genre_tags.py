
from django import template
register = template.Library()

GENRE_COLORS = {
    'action': 'g-danger',
    'adventure': 'g-warning',
    'comedy': 'g-warning',
    'drama': 'g-secondary',
    'epic fantasy': 'g-purple',
    'fantasy': 'g-purple',
    'historical': 'g-secondary',
    'horror': 'g-danger',
    'martial arts': 'g-dark',
    'mature': 'g-mature',
    'mecha': 'g-primary',
    'mystery': 'g-dark',
    'psychological': 'g-info',
    'romance': 'g-danger',
    'sci-fi': 'g-primary',
    'slice of life': 'g-success',
    'space fantasy': 'g-purple',
    'sports': 'g-success',
    'supernatural': 'g-info',
    'tragedy': 'g-secondary',
    'wuxia': 'g-dark',
    'xianxia': 'g-info',
    'xuanhuan': 'g-primary',
}


@register.filter
def genre_color(genre_name):
    return GENRE_COLORS.get(genre_name.lower(), 'g-default')