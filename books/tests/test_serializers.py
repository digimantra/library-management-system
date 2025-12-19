import pytest
from datetime import date
from books.models import Book
from books.serializers import BookListSerializer, BookDetailSerializer, BookCreateSerializer


@pytest.mark.django_db
class TestBookListSerializer:
    """Tests for BookListSerializer."""

    @pytest.fixture
    def book(self):
        return Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=200,
            published_date=date(2023, 1, 1),
            genre='fiction',
            total_copies=5,
            available_copies=3
        )

    def test_serializes_list_fields(self, book):
        """Test serializer includes expected list fields."""
        serializer = BookListSerializer(book)
        data = serializer.data
        
        assert data['title'] == 'Test Book'
        assert data['author'] == 'Test Author'
        assert data['isbn'] == '1234567890123'
        assert data['genre'] == 'fiction'
        assert data['available_copies'] == 3
        assert data['is_available'] is True

    def test_is_available_false_when_no_copies(self, book):
        """Test is_available is False when no copies available."""
        book.available_copies = 0
        book.save()
        
        serializer = BookListSerializer(book)
        assert serializer.data['is_available'] is False


@pytest.mark.django_db
class TestBookDetailSerializer:
    """Tests for BookDetailSerializer."""

    @pytest.fixture
    def book(self):
        return Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=200,
            published_date=date(2023, 1, 1),
            genre='fiction',
            description='A test book description',
            total_copies=5,
            available_copies=3
        )

    def test_serializes_detail_fields(self, book):
        """Test serializer includes all detail fields."""
        serializer = BookDetailSerializer(book)
        data = serializer.data
        
        assert data['title'] == 'Test Book'
        assert data['description'] == 'A test book description'
        assert data['page_count'] == 200
        assert data['total_copies'] == 5
        assert 'created_at' in data
        assert 'updated_at' in data


@pytest.mark.django_db
class TestBookCreateSerializer:
    """Tests for BookCreateSerializer."""

    def test_valid_data(self):
        """Test serializer with valid data."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'non-fiction',
            'total_copies': 3,
            'available_copies': 3
        }
        serializer = BookCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_available_copies_exceeds_total(self):
        """Test available_copies cannot exceed total_copies."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction',
            'total_copies': 3,
            'available_copies': 5
        }
        serializer = BookCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'available_copies' in serializer.errors

    def test_creates_book(self):
        """Test serializer creates book correctly."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction',
            'total_copies': 3
        }
        serializer = BookCreateSerializer(data=data)
        assert serializer.is_valid()
        book = serializer.save()
        
        assert book.title == 'New Book'
        assert book.available_copies == 3  # Defaults to total_copies

    def test_default_available_copies(self):
        """Test available_copies defaults to total_copies."""
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction',
            'total_copies': 5
        }
        serializer = BookCreateSerializer(data=data)
        assert serializer.is_valid()
        book = serializer.save()
        
        assert book.available_copies == 5
