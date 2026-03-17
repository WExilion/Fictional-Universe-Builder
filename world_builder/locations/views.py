from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from common.mixins import ConfirmDeleteViewMixin, MessageCreateUpdateViewMixin, LocationObjectViewMixin
from locations.forms import LocationCreateForm, LocationUpdateForm, LocationDeleteForm, SearchForm
from locations.models import Location


# Create your views here.
class LocationListView(ListView):
    model = Location
    template_name = 'locations/location-list.html'
    context_object_name = 'locations'
    extra_context = {'page_title': 'Locations'}
    paginate_by = 20

    def get_queryset(self):
        self.form = SearchForm(self.request.GET)
        queryset = Location.objects.select_related('universe', 'parent_location')

        if self.form.is_valid():
            search = self.form.cleaned_data.get('search')
            universe = self.form.cleaned_data.get('universe')
            if search:
                queryset = queryset.filter(name__icontains=search)
            if universe:
                queryset = queryset.filter(universe=universe).distinct()

        sort = self.request.GET.get('sort', '-created_at')
        allowed_sorts = {
            'name': 'name',
            '-created_at': '-created_at',
        }

        return queryset.order_by(allowed_sorts.get(sort, '-created_at'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['sort'] = self.request.GET.get('sort', '-created_at')
        return context

class LocationDetailView(LocationObjectViewMixin,DetailView):
    model = Location
    template_name = "locations/location-detail.html"
    context_object_name = 'location'

    def get_queryset(self):
        return Location.objects.select_related(
            'universe',
            'parent_location',
            'parent_location__parent_location',
        ).prefetch_related(
            'sub_locations',
            'characters'
        )


class LocationCreateView(MessageCreateUpdateViewMixin, CreateView):
    model = Location
    form_class = LocationCreateForm
    template_name = "locations/location-form.html"
    success_url = reverse_lazy('locations:list')
    success_message_action = 'created'

class LocationUpdateView(LocationObjectViewMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Location
    form_class = LocationUpdateForm
    template_name = "locations/location-form.html"
    success_message_action = 'updated'

    def get_success_url(self):
        return reverse_lazy('locations:detail', kwargs={
            'slug': self.object.slug,
            'universe_slug': self.object.universe.slug
        })


class LocationDeleteView(LocationObjectViewMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Location
    form_class = LocationDeleteForm
    template_name = "locations/location-delete.html"
    success_url = reverse_lazy('locations:list')