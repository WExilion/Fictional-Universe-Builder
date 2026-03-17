from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from common.mixins import ConfirmDeleteViewMixin, MessageCreateUpdateViewMixin
from universes.forms import UniverseCreateForm, SearchForm, UniverseUpdateForm, UniverseDeleteForm
from universes.models import Universe


# Create your views here.
class UniverseListView(ListView):
    model = Universe
    template_name = 'universes/universe-list.html'
    context_object_name = 'universes'
    extra_context = {'page_title': 'Universes'}
    paginate_by = 9


    def get_queryset(self):
        self.form = SearchForm(self.request.GET)
        queryset = Universe.objects.prefetch_related('genres')

        if self.form.is_valid():
            search = self.form.cleaned_data.get('search')
            genre = self.form.cleaned_data.get('genre')
            if search:
                queryset = queryset.filter(name__icontains=search).distinct()
            if genre:
                queryset = queryset.filter(genres=genre).distinct()

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


class UniverseDetailView(DetailView):
    model = Universe
    template_name = "universes/universe-detail.html"

    def get_queryset(self):
        return Universe.objects.prefetch_related('genres', 'characters', 'locations')

class UniverseCreateView(MessageCreateUpdateViewMixin, CreateView):
    model = Universe
    form_class = UniverseCreateForm
    template_name = "universes/universe-form.html"
    success_url = reverse_lazy('universes:list')
    success_message_action = 'created'

class UniverseUpdateView(MessageCreateUpdateViewMixin, UpdateView):
    model = Universe
    form_class = UniverseUpdateForm
    template_name = "universes/universe-form.html"
    success_message_action = 'updated'
    
    def get_success_url(self):
        return reverse_lazy('universes:detail', kwargs={'slug': self.object.slug})


class UniverseDeleteView(ConfirmDeleteViewMixin, DeleteView):
    model = Universe
    form_class = UniverseDeleteForm
    template_name = "universes/universe-delete.html"
    success_url = reverse_lazy('universes:list')


    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     form = self.get_form()
    #     if form.is_valid():
    #         name = self.object.name
    #         self.object.delete()
    #         messages.success(request, f'Universe "{name}" was deleted successfully.')
    #         return redirect(self.get_success_url())
    #         # return self.delete(request, *args, **kwargs)
    #     else:
    #         messages.error(request, 'You must confirm before deleting.')
    #         return self.get(request, *args, **kwargs)
