from django.shortcuts import render
from django.views.generic import TemplateView

from characters.models import Character
from locations.models import Location
from stories.models import Story
from universes.models import Universe

# Create your views here.
class HomeView(TemplateView):
    template_name = 'common/home.html'
    extra_context = {'page_title': 'Home'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['universe_count'] = Universe.objects.count()
        context['character_count'] = Character.objects.count()
        context['location_count'] = Location.objects.count()
        context['story_count'] = Story.objects.count()
        context['recent_universes'] = Universe.objects.order_by('-created_at')[:3]
        return context


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_403(request, exception=None):
    return render(request, '403.html', status=403)


def custom_400(request, exception=None):
    return render(request, '400.html', status=400)


def custom_500(request):
    return render(request, '500.html', status=500)


