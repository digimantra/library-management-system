import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from books.models import Book


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!'
    )


@pytest.fixture
def book():
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


@pytest.fixture
def books():
    """Create multiple books for filtering tests."""
    return [
        Book.objects.create(
            title='Python Programming',
            author='John Doe',
            isbn='1111111111111',
            page_count=400,
            published_date=date(2023, 1, 1),
            genre='technology',
            total_copies=3,
            available_copies=2
        ),
        Book.objects.create(
            title='Django Web Development',
            author='Jane Smith',
            isbn='2222222222222',
            page_count=350,
            published_date=date(2022, 6, 15),
            genre='technology',
            total_copies=2,
            available_copies=0
        ),
        Book.objects.create(
            title='The Great Novel',
            author='Famous Author',
            isbn='3333333333333',
            page_count=250,
            published_date=date(2021, 3, 20),
            genre='fiction',
            total_copies=5,
            available_copies=5
        ),
    ]


@pytest.mark.django_db
class TestBookViewSet:
    """Tests for BookViewSet."""

    def test_list_books_unauthenticated(self, api_client, book):
        """Test unauthenticated users can list books."""
        url = reverse('book-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_list_books_authenticated(self, api_client, user, book):
        """Test authenticated users can list books."""
        api_client.force_authenticate(user=user)
        url = reverse('book-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_book(self, api_client, book):
        """Test retrieving a single book."""
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Book'

    def test_create_book_as_admin(self, api_client, admin_user):
        """Test admin can create a book."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction',
            'total_copies': 3
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(isbn='9876543210123').exists()

    def test_create_book_as_regular_user(self, api_client, user):
        """Test regular user cannot create a book."""
        api_client.force_authenticate(user=user)
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_book_unauthenticated(self, api_client):
        """Test unauthenticated user cannot create a book."""
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'published_date': '2023-06-15',
            'genre': 'fiction'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_book_as_admin(self, api_client, admin_user, book):
        """Test admin can update a book."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('book-detail', kwargs={'pk': book.pk})
        data = {'title': 'Updated Title'}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == 'Updated Title'

    def test_delete_book_as_admin(self, api_client, admin_user, book):
        """Test admin can delete a book."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(pk=book.pk).exists()


@pytest.mark.django_db
class TestBookFiltering:
    """Tests for book filtering functionality."""

    def test_filter_by_title(self, api_client, books):
        """Test filtering books by title."""
        url = reverse('book-list')
        response = api_client.get(url, {'title': 'Python'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Python Programming'

    def test_filter_by_author(self, api_client, books):
        """Test filtering books by author."""
        url = reverse('book-list')
        response = api_client.get(url, {'author': 'John'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_filter_by_genre(self, api_client, books):
        """Test filtering books by genre."""
        url = reverse('book-list')
        response = api_client.get(url, {'genre': 'technology'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_filter_by_availability(self, api_client, books):
        """Test filtering books by availability."""
        url = reverse('book-list')
        response = api_client.get(url, {'is_available': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        # Only Python Programming and The Great Novel are available
        assert len(response.data['results']) == 2

    def test_search_books(self, api_client, books):
        """Test searching books."""
        url = reverse('book-list')
        response = api_client.get(url, {'search': 'Django'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestBookPagination:
    """Tests for book pagination."""

    def test_pagination_default(self, api_client):
        """Test default pagination."""
        # Create 15 books
        for i in range(15):
            Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i}',
                isbn=f'{1000000000000 + i}',
                page_count=100,
                published_date=date(2023, 1, 1),
                genre='fiction'
            )
        
        url = reverse('book-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10  # Default page size
        assert response.data['count'] == 15
        assert response.data['next'] is not None

    def test_pagination_second_page(self, api_client):
        """Test accessing second page."""
        for i in range(15):
            Book.objects.create(
                title=f'Book {i}',
                author=f'Author {i}',
                isbn=f'{1000000000000 + i}',
                page_count=100,
                published_date=date(2023, 1, 1),
                genre='fiction'
            )
        
        url = reverse('book-list')
        response = api_client.get(url, {'page': 2})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
