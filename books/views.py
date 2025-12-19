from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Book
from .serializers import BookListSerializer, BookDetailSerializer, BookCreateSerializer
from .filters import BookFilter
from accounts.permissions import IsAdminOrReadOnly


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing books.
    
    Anonymous users can browse books.
    Authenticated users can browse books.
    Admin users can create, update, and delete books.
    """
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'isbn', 'description']
    ordering_fields = ['title', 'author', 'published_date', 'page_count', 'available_copies']
    ordering = ['title']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BookListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return BookCreateSerializer
        return BookDetailSerializer

    @swagger_auto_schema(
        operation_description="List all books with optional filtering and pagination",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Filter by title (partial match)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'author', openapi.IN_QUERY,
                description="Filter by author (partial match)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'genre', openapi.IN_QUERY,
                description="Filter by genre",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_available', openapi.IN_QUERY,
                description="Filter by availability",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search in title, author, ISBN, description",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new book (Admin only)",
        responses={201: BookDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve book details"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a book (Admin only)",
        responses={200: BookDetailSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a book (Admin only)"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
