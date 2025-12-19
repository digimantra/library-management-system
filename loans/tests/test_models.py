import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from books.models import Book
from loans.models import Loan


@pytest.mark.django_db
class TestLoanModel:
    """Tests for Loan model."""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

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

    @pytest.fixture
    def loan(self, user, book):
        return Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )

    def test_loan_creation(self, loan, user, book):
        """Test loan is created correctly."""
        assert loan.user == user
        assert loan.book == book
        assert loan.status == 'active'
        assert loan.returned_date is None

    def test_loan_str_representation(self, loan):
        """Test string representation of Loan."""
        expected = f"{loan.user.username} - {loan.book.title} (active)"
        assert str(loan) == expected

    def test_default_due_date(self, user, book):
        """Test default due date is 14 days from now."""
        loan = Loan.objects.create(user=user, book=book)
        expected_due = timezone.now() + timedelta(days=14)
        
        # Allow 1 second tolerance
        assert abs((loan.due_date - expected_due).total_seconds()) < 1

    def test_is_overdue_false_when_not_overdue(self, user, book):
        """Test is_overdue returns False for active loan not overdue."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=7)
        )
        assert loan.is_overdue is False

    def test_is_overdue_true_when_past_due(self, user, book):
        """Test is_overdue returns True when past due date."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() - timedelta(days=1)
        )
        assert loan.is_overdue is True

    def test_is_overdue_false_when_returned(self, user, book):
        """Test is_overdue returns False for returned loans."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() - timedelta(days=1),
            status='returned'
        )
        assert loan.is_overdue is False

    def test_return_book_success(self, loan, book):
        """Test successful book return."""
        initial_copies = book.available_copies
        book.borrow()  # Simulate borrowing first
        book.refresh_from_db()
        
        result = loan.return_book()
        
        assert result is True
        assert loan.status == 'returned'
        assert loan.returned_date is not None
        
        book.refresh_from_db()
        assert book.available_copies == initial_copies

    def test_return_book_failure_already_returned(self, loan):
        """Test return_book fails if already returned."""
        loan.status = 'returned'
        loan.save()
        
        result = loan.return_book()
        assert result is False

    def test_get_active_loans_count(self, user, book):
        """Test get_active_loans_count returns correct count."""
        # Create 2 active loans
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        book2 = Book.objects.create(
            title='Another Book',
            author='Author',
            isbn='9876543210123',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        Loan.objects.create(
            user=user,
            book=book2,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        count = Loan.get_active_loans_count(user)
        assert count == 2

    def test_has_active_loan_true(self, loan, user, book):
        """Test has_active_loan returns True when user has active loan."""
        assert Loan.has_active_loan(user, book.id) is True

    def test_has_active_loan_false(self, user, book):
        """Test has_active_loan returns False when no active loan."""
        assert Loan.has_active_loan(user, book.id) is False

    def test_update_status_marks_overdue(self, user, book):
        """Test update_status marks active loan as overdue."""
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() - timedelta(days=1)
        )
        loan.update_status()
        
        assert loan.status == 'overdue'

    def test_ordering(self, user, book):
        """Test loans are ordered by borrowed_date descending."""
        loan1 = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        book2 = Book.objects.create(
            title='Another Book',
            author='Author',
            isbn='9876543210123',
            page_count=100,
            published_date=date(2023, 1, 1)
        )
        loan2 = Loan.objects.create(
            user=user,
            book=book2,
            due_date=timezone.now() + timedelta(days=14)
        )
        
        loans = list(Loan.objects.all())
        assert loans[0] == loan2  # Most recent first
        assert loans[1] == loan1
