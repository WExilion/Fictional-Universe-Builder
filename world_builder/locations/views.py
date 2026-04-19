from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from common.choices import SORT_OPTIONS
from common.mixins import CanManageObjectRequiredMixin, SetOwnerMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, \
    MessageCreateUpdateViewMixin, ConfirmDeleteViewMixin, CanManageObjectContextMixin
from locations.forms import LocationCreateForm, LocationUpdateForm, LocationDeleteForm, SearchForm
from locations.models import Location


# Create your views here.
class LocationListView(ListView):
    model = Location
    template_name = 'locations/location-list.html'
    context_object_name = 'locations'
    extra_context = {'page_title': 'Locations'}
    paginate_by = 20

    def get_search_form(self):
        if not hasattr(self, '_search_form'):
            data = self.request.GET.copy()
            if 'sort' not in data:
                data['sort'] = '-updated'
            self._search_form = SearchForm(data)
        return self._search_form

    def get_queryset(self):
        qs = super().get_queryset().select_related('universe', 'parent_location')

        form = self.get_search_form()
        if form.is_valid():
            search = form.cleaned_data.get('search')
            universe = form.cleaned_data.get('universe')
            sort = form.cleaned_data.get('sort')
            if search:
                qs = qs.filter(name__icontains=search)
            if universe:
                qs = qs.filter(universe__name__icontains=universe)
            if sort and sort in SORT_OPTIONS:
                qs = qs.order_by(SORT_OPTIONS[sort])
            else:
                qs = qs.order_by('-updated_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_search_form()
        return context

class LocationDetailView(UniverseSlugObjectMixin, CanManageObjectContextMixin, DetailView):
    model = Location
    template_name = "locations/location-detail.html"
    context_object_name = 'location'
    def get_queryset(self):
        return super().get_queryset().select_related(
            'parent_location',
            'parent_location__universe',
        ).prefetch_related(
            'sub_locations',
            'characters'
        )

class LocationCreateView(LoginRequiredMixin, SetOwnerMixin, FilterOwnerFormMixin, MessageCreateUpdateViewMixin, CreateView):
    model = Location
    form_class = LocationCreateForm
    template_name = "locations/location-form.html"
    success_url = reverse_lazy('locations:list')
    success_message_action = 'created'

class LocationUpdateView(LoginRequiredMixin, CanManageObjectRequiredMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Location
    form_class = LocationUpdateForm
    template_name = "locations/location-form.html"
    success_message_action = 'updated'
    def get_queryset(self):
        return super().get_queryset().select_related('parent_location')



class LocationDeleteView(LoginRequiredMixin, CanManageObjectRequiredMixin, UniverseSlugObjectMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Location
    form_class = LocationDeleteForm
    template_name = "locations/location-delete.html"
    context_object_name = 'location'
    success_url = reverse_lazy('locations:list')