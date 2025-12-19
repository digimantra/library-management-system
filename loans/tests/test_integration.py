"""
Integration tests for complete user flows.
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from books.models import Book
from loans.models import Loan


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def book():
    return Book.objects.create(
        title='Integration Test Book',
        author='Test Author',
        isbn='1234567890123',
        page_count=200,
        published_date=date(2023, 1, 1),
        genre='fiction',
        total_copies=3,
        available_copies=3
    )


@pytest.mark.django_db
class TestCompleteUserFlow:
    """
    Integration tests for complete user flows:
    Register -> Login -> Browse -> Borrow -> Return
    """

    def test_complete_user_journey(self, api_client, book):
        """Test complete user journey from registration to book return."""
        
        # Step 1: Register new user
        register_url = reverse('register')
        register_data = {
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'Integration',
            'last_name': 'User'
        }
        response = api_client.post(register_url, register_data)
        assert response.status_code == status.HTTP_201_CREATED
        access_token = response.data['tokens']['access']
        
        # Step 2: Use token for authenticated requests
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 3: Browse books (also works without auth)
        books_url = reverse('book-list')
        response = api_client.get(books_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        
        # Step 4: View book details
        book_detail_url = reverse('book-detail', kwargs={'pk': book.pk})
        response = api_client.get(book_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Integration Test Book'
        assert response.data['available_copies'] == 3
        
        # Step 5: Borrow the book
        borrow_url = reverse('borrow-book')
        borrow_data = {'book_id': book.id}
        response = api_client.post(borrow_url, borrow_data)
        assert response.status_code == status.HTTP_201_CREATED
        loan_id = response.data['loan']['id']
        
        # Verify book availability decreased
        book.refresh_from_db()
        assert book.available_copies == 2
        
        # Step 6: View active loans
        active_loans_url = reverse('active-loans')
        response = api_client.get(active_loans_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == loan_id
        
        # Step 7: Return the book
        return_url = reverse('return-book')
        return_data = {'loan_id': loan_id}
        response = api_client.post(return_url, return_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify book availability restored
        book.refresh_from_db()
        assert book.available_copies == 3
        
        # Step 8: Verify loan history shows returned
        history_url = reverse('loan-history')
        response = api_client.get(history_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['status'] == 'returned'


@pytest.mark.django_db
class TestAnonymousUserFlow:
    """Test anonymous user access patterns."""

    def test_anonymous_can_browse_books(self, api_client, book):
        """Test anonymous users can browse books."""
        url = reverse('book-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_anonymous_can_view_book_details(self, api_client, book):
        """Test anonymous users can view book details."""
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Integration Test Book'

    def test_anonymous_can_search_books(self, api_client, book):
        """Test anonymous users can search books."""
        url = reverse('book-list')
        response = api_client.get(url, {'search': 'Integration'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_anonymous_cannot_borrow(self, api_client, book):
        """Test anonymous users cannot borrow books."""
        url = reverse('borrow-book')
        response = api_client.post(url, {'book_id': book.id})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_cannot_access_loan_history(self, api_client):
        """Test anonymous users cannot access loan history."""
        url = reverse('loan-history')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAdminFlow:
    """Test admin user flows."""

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )

    def test_admin_can_create_book(self, api_client, admin_user):
        """Test admin can create a new book."""
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('book-list')
        data = {
            'title': 'Admin Created Book',
            'author': 'Admin Author',
            'isbn': '9999999999999',
            'page_count': 150,
            'published_date': '2023-12-01',
            'genre': 'science',
            'total_copies': 5
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(isbn='9999999999999').exists()

    def test_admin_can_update_book(self, api_client, admin_user, book):
        """Test admin can update a book."""
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('book-detail', kwargs={'pk': book.pk})
        data = {'title': 'Updated Book Title', 'total_copies': 10}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == 'Updated Book Title'
        assert book.total_copies == 10

    def test_admin_can_delete_book(self, api_client, admin_user, book):
        """Test admin can delete a book."""
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(pk=book.pk).exists()

    def test_admin_can_view_all_loans(self, api_client, admin_user, book):
        """Test admin can view all loans in the system."""
        # Create a loan for a regular user
        user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        book.borrow()
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('admin-loan-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_admin_can_manage_users(self, api_client, admin_user):
        """Test admin can manage users."""
        # Create a regular user
        User.objects.create_user('testuser', 'test@example.com', 'pass123')
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2  # admin + testuser


@pytest.mark.django_db
class TestConcurrentBorrowing:
    """Test edge cases with concurrent borrowing."""

    def test_last_copy_borrow(self, api_client, book):
        """Test borrowing the last available copy."""
        book.available_copies = 1
        book.save()
        
        user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        api_client.force_authenticate(user=user)
        
        url = reverse('borrow-book')
        response = api_client.post(url, {'book_id': book.id})
        
        assert response.status_code == status.HTTP_201_CREATED
        
        book.refresh_from_db()
        assert book.available_copies == 0
        assert book.is_available is False

    def test_cannot_borrow_when_no_copies(self, api_client, book):
        """Test cannot borrow when no copies available."""
        book.available_copies = 0
        book.save()
        
        user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        api_client.force_authenticate(user=user)
        
        url = reverse('borrow-book')
        response = api_client.post(url, {'book_id': book.id})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multiple_users_borrow_same_book(self, api_client, book):
        """Test multiple users can borrow the same book (different copies)."""
        user1 = User.objects.create_user('user1', 'user1@example.com', 'pass123')
        user2 = User.objects.create_user('user2', 'user2@example.com', 'pass123')
        
        # User 1 borrows
        api_client.force_authenticate(user=user1)
        url = reverse('borrow-book')
        response = api_client.post(url, {'book_id': book.id})
        assert response.status_code == status.HTTP_201_CREATED
        
        # User 2 borrows
        api_client.force_authenticate(user=user2)
        response = api_client.post(url, {'book_id': book.id})
        assert response.status_code == status.HTTP_201_CREATED
        
        book.refresh_from_db()
        assert book.available_copies == 1
        assert Loan.objects.filter(book=book, status='active').count() == 2
