from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from universes.models import Universe
from common.permissions import IsOwnerOrModeratorOrReadOnly
from universes.serializers import UniverseSerializer


SORT_OPTIONS = {
    'name': 'name',
    '-name': '-name',
    'created': 'created_at',
    '-created': '-created_at',
    'updated': 'updated_at',
    '-updated': '-updated_at',
}


class UniverseListCreateApiView(generics.ListCreateAPIView):
    serializer_class = UniverseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Universe.objects.select_related('owner').prefetch_related('genres')

        search = self.request.query_params.get('search')
        genre = self.request.query_params.get('genre')
        sort = self.request.query_params.get('sort')


        if search:
            queryset = queryset.filter(name__icontains=search)
        if genre:
            queryset = queryset.filter(genres__name__iexact=genre)
        if sort and sort in SORT_OPTIONS:
            queryset = queryset.order_by(SORT_OPTIONS[sort])

        return queryset.distinct()


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class UniverseDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UniverseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrModeratorOrReadOnly]
    lookup_field = 'slug'
    def get_queryset(self):
        return Universe.objects.select_related('owner').prefetch_related('genres')