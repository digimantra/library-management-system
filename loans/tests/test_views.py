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
def loan(user, book):
    book.borrow()
    return Loan.objects.create(
        user=user,
        book=book,
        due_date=timezone.now() + timedelta(days=14)
    )


@pytest.mark.django_db
class TestBorrowBookView:
    """Tests for borrow book endpoint."""

    def test_borrow_success(self, api_client, user, book):
        """Test successful book borrowing."""
        api_client.force_authenticate(user=user)
        url = reverse('borrow-book')
        data = {'book_id': book.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'loan' in response.data
        assert response.data['message'] == 'Book borrowed successfully.'
        
        book.refresh_from_db()
        assert book.available_copies == 4

    def test_borrow_unauthenticated(self, api_client, book):
        """Test unauthenticated user cannot borrow."""
        url = reverse('borrow-book')
        data = {'book_id': book.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_borrow_unavailable_book(self, api_client, user, book):
        """Test cannot borrow unavailable book."""
        book.available_copies = 0
        book.save()
        
        api_client.force_authenticate(user=user)
        url = reverse('borrow-book')
        data = {'book_id': book.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_borrow_already_borrowed(self, api_client, user, book, loan):
        """Test cannot borrow same book twice."""
        api_client.force_authenticate(user=user)
        url = reverse('borrow-book')
        data = {'book_id': book.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestReturnBookView:
    """Tests for return book endpoint."""

    def test_return_success(self, api_client, user, book, loan):
        """Test successful book return."""
        api_client.force_authenticate(user=user)
        url = reverse('return-book')
        data = {'loan_id': loan.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Book returned successfully.'
        
        loan.refresh_from_db()
        assert loan.status == 'returned'
        
        book.refresh_from_db()
        assert book.available_copies == 5

    def test_return_unauthenticated(self, api_client, loan):
        """Test unauthenticated user cannot return."""
        url = reverse('return-book')
        data = {'loan_id': loan.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_return_other_users_loan(self, api_client, book, loan):
        """Test user cannot return another user's loan."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        
        api_client.force_authenticate(user=other_user)
        url = reverse('return-book')
        data = {'loan_id': loan.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_return_any_loan(self, api_client, admin_user, loan):
        """Test admin can return any user's loan."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('return-book')
        data = {'loan_id': loan.id}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLoanHistoryView:
    """Tests for loan history endpoint."""

    def test_get_loan_history(self, api_client, user, loan):
        """Test getting user's loan history."""
        api_client.force_authenticate(user=user)
        url = reverse('loan-history')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_filter_by_status(self, api_client, user, loan):
        """Test filtering loan history by status."""
        api_client.force_authenticate(user=user)
        url = reverse('loan-history')
        
        response = api_client.get(url, {'status': 'active'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_unauthenticated_access(self, api_client):
        """Test unauthenticated user cannot access loan history."""
        url = reverse('loan-history')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestActiveLoansView:
    """Tests for active loans endpoint."""

    def test_get_active_loans(self, api_client, user, loan):
        """Test getting user's active loans."""
        api_client.force_authenticate(user=user)
        url = reverse('active-loans')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_excludes_returned_loans(self, api_client, user, book):
        """Test returned loans are not included."""
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14),
            status='returned',
            returned_date=timezone.now()
        )
        
        api_client.force_authenticate(user=user)
        url = reverse('active-loans')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestAdminLoanViewSet:
    """Tests for admin loan management endpoint."""

    def test_admin_can_list_all_loans(self, api_client, admin_user, loan):
        """Test admin can list all loans."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('admin-loan-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_regular_user_cannot_access(self, api_client, user, loan):
        """Test regular user cannot access admin endpoint."""
        api_client.force_authenticate(user=user)
        url = reverse('admin-loan-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
