from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError

from rest_framework import filters, viewsets, permissions, serializers
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from api.filters import TitleFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

from api.permissions import (
    IsAdminOrReadOnly,
    IsAuthenticatedOrOwnerOrReadOnly,
    IsAuthorOrModerOrAdmin
)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleSerializer, TitleCreateSerializer)

from .models import Category, Genre, Title, Review, Comment


class CustomMixin(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass


class CategoryViewSet(CustomMixin):
    """API для категорий."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def retrieve(self, request, slug=None):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, slug=None):
        return Response(status=status.HTTP_404_NOT_FOUND)


class GenreViewSet(CustomMixin):
    """API для жанров."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """API для произведений."""
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('name',)
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_permissions(self):

        # POST
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)

        # GET and GET LIST
        elif self.action == 'list' or  self.action == 'retrieve':
            return (permissions.AllowAny(),)

        # UPDATE or DELETE
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            return (permissions.IsAuthenticated(), IsAuthorOrModerOrAdmin(),)

    def get_queryset(self):

        titles = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )

        new_queryset = titles.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            serializer.save(author=self.request.user, titles=title)
        except IntegrityError:
            raise serializers.ValidationError('unique_together.')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_permissions(self):

        # POST
        if self.action == 'create':
            return (permissions.IsAuthenticated(),)

        # GET and GET LIST
        elif self.action == 'list' or  self.action == 'retrieve':
            return (permissions.AllowAny(),)

        # UPDATE or DELETE
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            return (permissions.IsAuthenticated(), IsAuthorOrModerOrAdmin(),)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        new_queryset = review.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, reviews=review)
