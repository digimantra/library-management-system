import pytest
from datetime import date
from django.core.exceptions import ValidationError
from books.models import Book


@pytest.mark.django_db
class TestBookModel:
    """Tests for Book model."""

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
            available_copies=5
        )

    def test_book_creation(self, book):
        """Test book is created correctly."""
        assert book.title == 'Test Book'
        assert book.author == 'Test Author'
        assert book.isbn == '1234567890123'
        assert book.page_count == 200
        assert book.genre == 'fiction'

    def test_book_str_representation(self, book):
        """Test string representation of Book."""
        assert str(book) == 'Test Book by Test Author'

    def test_is_available_property_true(self, book):
        """Test is_available returns True when copies are available."""
        assert book.is_available is True

    def test_is_available_property_false(self, book):
        """Test is_available returns False when no copies available."""
        book.available_copies = 0
        book.save()
        assert book.is_available is False

    def test_borrow_success(self, book):
        """Test successful book borrow."""
        initial_copies = book.available_copies
        result = book.borrow()
        
        book.refresh_from_db()
        assert result is True
        assert book.available_copies == initial_copies - 1

    def test_borrow_failure_no_copies(self, book):
        """Test borrow fails when no copies available."""
        book.available_copies = 0
        book.save()
        
        result = book.borrow()
        assert result is False

    def test_return_book_success(self, book):
        """Test successful book return."""
        book.available_copies = 3
        book.save()
        
        result = book.return_book()
        
        book.refresh_from_db()
        assert result is True
        assert book.available_copies == 4

    def test_return_book_failure_all_copies_available(self, book):
        """Test return fails when all copies already available."""
        result = book.return_book()
        assert result is False

    def test_available_copies_cannot_exceed_total(self, book):
        """Test available_copies is capped at total_copies on save."""
        book.available_copies = 10  # More than total_copies (5)
        book.save()
        
        book.refresh_from_db()
        assert book.available_copies == book.total_copies

    def test_isbn_10_digits_valid(self):
        """Test ISBN with 10 digits is valid."""
        book = Book(
            title='Test',
            author='Author',
            isbn='1234567890',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        book.full_clean()  # Should not raise

    def test_isbn_13_digits_valid(self):
        """Test ISBN with 13 digits is valid."""
        book = Book(
            title='Test',
            author='Author',
            isbn='1234567890123',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        book.full_clean()  # Should not raise

    def test_isbn_invalid_format(self):
        """Test ISBN with invalid format raises error."""
        book = Book(
            title='Test',
            author='Author',
            isbn='12345',  # Invalid length
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        with pytest.raises(ValidationError):
            book.full_clean()

    def test_ordering(self):
        """Test books are ordered by title."""
        Book.objects.create(
            title='Zebra Book',
            author='Author',
            isbn='1234567890123',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        Book.objects.create(
            title='Apple Book',
            author='Author',
            isbn='1234567890124',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        
        books = list(Book.objects.all())
        assert books[0].title == 'Apple Book'
        assert books[1].title == 'Zebra Book'
