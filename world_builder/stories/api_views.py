from django.db.models import Q
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from stories.models import Story
from stories.serializers import StorySerializer
from common.permissions import IsOwnerOrModeratorOrReadOnly

SORT_OPTIONS = {
    'title': 'title',
    '-title': '-title',
    'created': 'created_at',
    '-created': '-created_at',
    'updated': 'updated_at',
    '-updated': '-updated_at',
}

class StoryListCreateApiView(generics.ListCreateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        queryset = Story.objects.select_related('universe', 'owner').prefetch_related('characters')

        search = self.request.query_params.get('search')
        universe = self.request.query_params.get('universe')
        sort = self.request.query_params.get('sort')

        user = self.request.user

        if user.is_authenticated and (user.is_superuser or user.groups.filter(name='Moderators').exists()):
            queryset = queryset
        elif user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(owner=user))
        else:
            queryset = queryset.filter(is_published=True)


        if search:
            queryset = queryset.filter(title__icontains=search)
        if universe:
            queryset = queryset.filter(universe__name__icontains=universe)
        if sort and sort in SORT_OPTIONS:
            queryset = queryset.order_by(SORT_OPTIONS[sort])

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class StoryDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrModeratorOrReadOnly]

    def get_queryset(self):
        queryset = Story.objects.select_related('universe', 'owner').prefetch_related('characters')
        user = self.request.user

        if user.is_authenticated and (user.is_superuser or user.groups.filter(name='Moderators').exists()):
            return queryset

        if user.is_authenticated:
            return queryset.filter(Q(is_published=True) | Q(owner=user))

        return queryset.filter(is_published=True)


    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            universe__slug=self.kwargs['universe_slug'],
            slug=self.kwargs['slug'],
        )
        self.check_object_permissions(self.request, obj)
        return obj



