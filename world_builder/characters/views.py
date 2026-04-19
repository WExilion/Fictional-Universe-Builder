from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from characters.forms import CharacterUpdateForm, CharacterCreateForm, SearchForm, CharacterDeleteForm
from characters.models import Character
from common.choices import SORT_OPTIONS
from common.mixins import CanManageObjectRequiredMixin, SetOwnerMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, \
    MessageCreateUpdateViewMixin, ConfirmDeleteViewMixin, CanManageObjectContextMixin


# Create your views here.
class CharacterListView(ListView):
    model = Character
    template_name = 'characters/character-list.html'
    context_object_name = 'characters'
    extra_context = {'page_title': 'Characters'}
    paginate_by = 20

    def get_search_form(self):
        if not hasattr(self, '_search_form'):
            data = self.request.GET.copy()
            if 'sort' not in data:
                data['sort'] = '-updated'
            self._search_form = SearchForm(data)
        return self._search_form


    def get_queryset(self):
        self.form = SearchForm(self.request.GET) # noqa
        qs = super().get_queryset().select_related('universe')

        form = self.get_search_form()
        if form.is_valid():
            search = form.cleaned_data.get('search')
            universe = form.cleaned_data.get('universe')
            sort = form.cleaned_data.get('sort')
            if search:
                qs = qs.filter(
                    Q(first_name__icontains=search)
                    |
                    Q(last_name__icontains=search)
                ).distinct()
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


class CharacterDetailView(UniverseSlugObjectMixin, CanManageObjectContextMixin, DetailView):
    model = Character
    template_name = "characters/character-detail.html"
    context_object_name = 'character'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'location',
            'location__universe',
        )

class CharacterCreateView(LoginRequiredMixin, SetOwnerMixin, FilterOwnerFormMixin, MessageCreateUpdateViewMixin, CreateView):
    model = Character
    form_class = CharacterCreateForm
    template_name = "characters/character-form.html"
    success_url = reverse_lazy('characters:list')
    success_message_action = 'created'

class CharacterUpdateView(LoginRequiredMixin, CanManageObjectRequiredMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Character
    form_class = CharacterUpdateForm
    template_name = "characters/character-form.html"
    success_message_action = 'updated'
    permission_required = 'characters.change_character'

    def get_queryset(self):
        return super().get_queryset().select_related('location')


class CharacterDeleteView(LoginRequiredMixin, CanManageObjectRequiredMixin, UniverseSlugObjectMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Character
    form_class = CharacterDeleteForm
    template_name = "characters/character-delete.html"
    context_object_name = 'character'
    success_url = reverse_lazy('characters:list')
    permission_required = 'characters.delete_character'