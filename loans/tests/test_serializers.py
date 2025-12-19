import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from books.models import Book
from loans.models import Loan
from loans.serializers import (
    LoanSerializer,
    BorrowBookSerializer,
    ReturnBookSerializer
)


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
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
def request_factory():
    return APIRequestFactory()


@pytest.mark.django_db
class TestLoanSerializer:
    """Tests for LoanSerializer."""

    def test_serializes_loan_data(self, user, book):
        """Test serializer includes expected fields."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        serializer = LoanSerializer(loan)
        data = serializer.data
        
        assert data['username'] == 'testuser'
        assert 'book' in data
        assert 'borrowed_date' in data
        assert 'due_date' in data
        assert 'status' in data
        assert 'is_overdue' in data


@pytest.mark.django_db
class TestBorrowBookSerializer:
    """Tests for BorrowBookSerializer."""

    def test_valid_borrow_request(self, user, book, request_factory):
        """Test valid borrow request."""
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        data = {'book_id': book.id}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        
        assert serializer.is_valid(), serializer.errors

    def test_book_not_found(self, user, request_factory):
        """Test borrow request for non-existent book."""
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        data = {'book_id': 99999}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'book_id' in serializer.errors

    def test_book_not_available(self, user, book, request_factory):
        """Test borrow request for unavailable book."""
        book.available_copies = 0
        book.save()
        
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        data = {'book_id': book.id}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'book_id' in serializer.errors

    def test_already_borrowed(self, user, book, request_factory):
        """Test user cannot borrow same book twice."""
        # Create existing active loan
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        data = {'book_id': book.id}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'book_id' in serializer.errors

    def test_due_date_in_past(self, user, book, request_factory):
        """Test due date must be in the future."""
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        past_date = (timezone.now() - timedelta(days=1)).isoformat()
        data = {'book_id': book.id, 'due_date': past_date}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'due_date' in serializer.errors

    def test_creates_loan(self, user, book, request_factory):
        """Test serializer creates loan correctly."""
        request = request_factory.post('/api/loans/borrow/')
        request.user = user
        
        data = {'book_id': book.id}
        serializer = BorrowBookSerializer(data=data, context={'request': request})
        assert serializer.is_valid()
        
        loan = serializer.save()
        
        assert loan.user == user
        assert loan.book == book
        assert loan.status == 'active'
        
        book.refresh_from_db()
        assert book.available_copies == 4


@pytest.mark.django_db
class TestReturnBookSerializer:
    """Tests for ReturnBookSerializer."""

    def test_valid_return_request(self, user, book, request_factory):
        """Test valid return request."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        book.borrow()
        
        request = request_factory.post('/api/loans/return/')
        request.user = user
        
        data = {'loan_id': loan.id}
        serializer = ReturnBookSerializer(data=data, context={'request': request})
        
        assert serializer.is_valid(), serializer.errors

    def test_loan_not_found(self, user, request_factory):
        """Test return request for non-existent loan."""
        request = request_factory.post('/api/loans/return/')
        request.user = user
        
        data = {'loan_id': 99999}
        serializer = ReturnBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'loan_id' in serializer.errors

    def test_loan_belongs_to_different_user(self, user, book, request_factory):
        """Test user cannot return another user's loan."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        loan = Loan.objects.create(
            user=other_user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        request = request_factory.post('/api/loans/return/')
        request.user = user
        
        data = {'loan_id': loan.id}
        serializer = ReturnBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'loan_id' in serializer.errors

    def test_already_returned(self, user, book, request_factory):
        """Test cannot return already returned book."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14),
            status='returned',
            returned_date=timezone.now()
        )
        
        request = request_factory.post('/api/loans/return/')
        request.user = user
        
        data = {'loan_id': loan.id}
        serializer = ReturnBookSerializer(data=data, context={'request': request})
        
        assert not serializer.is_valid()
        assert 'loan_id' in serializer.errors
