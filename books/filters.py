import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    """Filter set for book queries."""
    
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter by title (case-insensitive, partial match)'
    )
    author = django_filters.CharFilter(
        field_name='author',
        lookup_expr='icontains',
        help_text='Filter by author (case-insensitive, partial match)'
    )
    isbn = django_filters.CharFilter(
        field_name='isbn',
        lookup_expr='exact',
        help_text='Filter by exact ISBN'
    )
    genre = django_filters.ChoiceFilter(
        field_name='genre',
        choices=Book.GENRE_CHOICES,
        help_text='Filter by genre'
    )
    is_available = django_filters.BooleanFilter(
        method='filter_available',
        help_text='Filter by availability'
    )
    published_after = django_filters.DateFilter(
        field_name='published_date',
        lookup_expr='gte',
        help_text='Filter books published after this date'
    )
    published_before = django_filters.DateFilter(
        field_name='published_date',
        lookup_expr='lte',
        help_text='Filter books published before this date'
    )
    min_pages = django_filters.NumberFilter(
        field_name='page_count',
        lookup_expr='gte',
        help_text='Filter by minimum page count'
    )
    max_pages = django_filters.NumberFilter(
        field_name='page_count',
        lookup_expr='lte',
        help_text='Filter by maximum page count'
    )

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'genre',
            'is_available', 'published_after', 'published_before',
            'min_pages', 'max_pages'
        ]

    def filter_available(self, queryset, name, value):
        """Filter by availability status."""
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset.filter(available_copies=0)
