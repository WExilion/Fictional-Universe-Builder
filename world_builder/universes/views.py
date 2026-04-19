from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from common.choices import SORT_OPTIONS
from common.mixins import CanManageObjectRequiredMixin, MessageCreateUpdateViewMixin, ConfirmDeleteViewMixin, \
    SetOwnerMixin, CanManageObjectContextMixin, UnpublishedAccessMixin
from universes.forms import UniverseCreateForm, SearchForm, UniverseUpdateForm, UniverseDeleteForm
from universes.models import Universe


# Create your views here.
class UniverseListView(ListView):
    model = Universe
    template_name = 'universes/universe-list.html'
    context_object_name = 'universes'
    extra_context = {'page_title': 'Universes'}
    paginate_by = 9

    def get_search_form(self):
        if not hasattr(self, '_search_form'):
            data = self.request.GET.copy()
            if 'sort' not in data:
                data['sort'] = '-updated'
            self._search_form = SearchForm(data)
        return self._search_form


    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('genres')
        form = self.get_search_form()
        if form.is_valid():
            search = form.cleaned_data.get('search')
            genre = form.cleaned_data.get('genre')
            sort = form.cleaned_data.get('sort')
            if search:
                qs = qs.filter(name__icontains=search)
            if genre:
                qs = qs.filter(genres=genre).distinct()
            if sort and sort in SORT_OPTIONS:
                qs = qs.order_by(SORT_OPTIONS[sort])
            else:
                qs = qs.order_by('-updated_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.get_search_form()
        return context


class UniverseDetailView(UnpublishedAccessMixin, CanManageObjectContextMixin, DetailView):
    model = Universe
    template_name = "universes/universe-detail.html"
    context_object_name = 'universe'
    def get_queryset(self):
        return super().get_queryset().prefetch_related('genres', 'characters', 'locations')

    def get_universe_stories(self):
        stories = self.object.stories.all()
        if self.can_view_unpublished():
            return stories
        if self.request.user.is_authenticated:
            return stories.filter(Q(is_published=True) | Q(owner=self.request.user))
        return stories.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["universe_stories"] = self.get_universe_stories()
        return context



class UniverseCreateView(LoginRequiredMixin, SetOwnerMixin, MessageCreateUpdateViewMixin, CreateView):
    model = Universe
    form_class = UniverseCreateForm
    template_name = "universes/universe-form.html"
    success_url = reverse_lazy('universes:list')
    success_message_action = 'created'

class UniverseUpdateView(LoginRequiredMixin, CanManageObjectRequiredMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Universe
    form_class = UniverseUpdateForm
    template_name = "universes/universe-form.html"
    success_message_action = 'updated'
    
    def get_success_url(self):
        return reverse_lazy('universes:detail', kwargs={'slug': self.object.slug})


class UniverseDeleteView(LoginRequiredMixin, CanManageObjectRequiredMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Universe
    form_class = UniverseDeleteForm
    template_name = "universes/universe-delete.html"
    context_object_name = 'universe'
    success_url = reverse_lazy('universes:list')