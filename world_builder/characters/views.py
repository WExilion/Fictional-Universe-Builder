from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from characters.forms import CharacterUpdateForm, CharacterCreateForm, SearchForm, CharacterDeleteForm
from characters.models import Character
from common.mixins import ConfirmDeleteViewMixin, MessageCreateUpdateViewMixin, CharacterObjectViewMixin


# Create your views here.
class CharacterListView(ListView):
    model = Character
    template_name = 'characters/character-list.html'
    context_object_name = 'characters'
    extra_context = {'page_title': 'Characters'}
    paginate_by = 20


    def get_queryset(self):
        self.form = SearchForm(self.request.GET)
        queryset = Character.objects.select_related('universe', 'location')

        if self.form.is_valid():
            search = self.form.cleaned_data.get('search')
            universe = self.form.cleaned_data.get('universe')
            if search:
                queryset = queryset.filter(
                    Q(first_name__icontains=search)
                    |
                    Q(last_name__icontains=search)
                ).distinct()
            if universe:
                queryset = queryset.filter(universe=universe).distinct()

        sort = self.request.GET.get('sort', '-created_at')
        allowed_sorts = {
            'first_name': 'first_name',
            '-created_at': '-created_at',
        }
        queryset = queryset.order_by(allowed_sorts.get(sort, '-created_at'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['sort'] = self.request.GET.get('sort', '-created_at')
        return context


class CharacterDetailView(CharacterObjectViewMixin, DetailView):
    model = Character
    template_name = "characters/character-detail.html"
    def get_queryset(self):
        return Character.objects.select_related(
            'universe',
            'location',
            'location__parent_location',
            'location__parent_location__parent_location',
        )
class CharacterCreateView(MessageCreateUpdateViewMixin, CreateView):
    model = Character
    form_class = CharacterCreateForm
    template_name = "characters/character-form.html"
    success_url = reverse_lazy('characters:list')
    success_message_action = 'created'


class CharacterUpdateView(CharacterObjectViewMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Character
    form_class = CharacterUpdateForm
    template_name = "characters/character-form.html"
    success_message_action = 'updated'

    def get_success_url(self):
        return reverse_lazy('characters:detail', kwargs={
            'slug': self.object.slug,
            'universe_slug': self.object.universe.slug
        })


class CharacterDeleteView(CharacterObjectViewMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Character
    form_class = CharacterDeleteForm
    template_name = "characters/character-delete.html"
    success_url = reverse_lazy('characters:list')
