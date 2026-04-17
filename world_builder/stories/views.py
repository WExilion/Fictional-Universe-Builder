from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from common.mixins import SetOwnerMixin, CanManageObjectRequiredMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, \
    ConfirmDeleteViewMixin, MessageCreateUpdateViewMixin, CanManageObjectContextMixin, UnpublishedAccessMixin
from common.choices import SORT_OPTIONS
from stories.forms import StoryCreateForm, StoryUpdateForm, StoryDeleteForm, SearchForm
from stories.models import Story


# Create your views here.
class StoryListView(UnpublishedAccessMixin, ListView):
    model = Story
    template_name = 'stories/story-list.html'
    context_object_name = 'stories'
    extra_context = {'page_title': 'Stories'}
    paginate_by = 20
    def get_search_form(self):
        if not hasattr(self, '_search_form'):
            data = self.request.GET.copy()
            if 'sort' not in data:
                data['sort'] = '-updated'
            self._search_form = SearchForm(data)
        return self._search_form

    def get_queryset(self):
        qs = super().get_queryset().select_related("universe", "owner")

        if not self.can_view_unpublished():
            if self.request.user.is_authenticated:
                qs = qs.filter(Q(is_published=True) | Q(owner=self.request.user))
            else:
                qs = qs.filter(is_published=True)


        form = self.get_search_form()
        if form.is_valid():
            search = form.cleaned_data.get('search')
            universe = form.cleaned_data.get('universe')
            sort = form.cleaned_data.get('sort')
            if search:
                qs = qs.filter(title__icontains=search)
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



class StoryDetailView(UniverseSlugObjectMixin, UnpublishedAccessMixin, CanManageObjectContextMixin, DetailView):
    model = Story
    template_name = "stories/story-detail.html"
    context_object_name = 'story'
    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('characters')
        if self.can_view_unpublished():
            return qs
        if self.request.user.is_authenticated:
            return qs.filter(Q(is_published=True) | Q(owner=self.request.user))
        return qs.filter(is_published=True)


class StoryCreateView(LoginRequiredMixin, SetOwnerMixin, FilterOwnerFormMixin, MessageCreateUpdateViewMixin, CreateView):
    model = Story
    form_class = StoryCreateForm
    template_name = "stories/story-form.html"
    success_url = reverse_lazy('stories:list')
    success_message_action = 'created'

class StoryUpdateView(LoginRequiredMixin, CanManageObjectRequiredMixin, FilterOwnerFormMixin, UniverseSlugObjectMixin, MessageCreateUpdateViewMixin, UpdateView):
    model = Story
    form_class = StoryUpdateForm
    template_name = "stories/story-form.html"
    success_message_action = 'updated'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('characters')

class StoryDeleteView(LoginRequiredMixin, CanManageObjectRequiredMixin, UniverseSlugObjectMixin, ConfirmDeleteViewMixin, DeleteView):
    model = Story
    form_class = StoryDeleteForm
    template_name = "stories/story-delete.html"
    context_object_name = 'story'
    success_url = reverse_lazy('stories:list')