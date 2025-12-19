import pytest
from django.contrib.auth.models import User
from accounts.models import UserProfile


@pytest.mark.django_db
class TestUserProfileModel:
    """Tests for UserProfile model."""

    def test_profile_created_on_user_creation(self):
        """Test that UserProfile is created when a User is created."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, UserProfile)

    def test_profile_str_representation(self):
        """Test string representation of UserProfile."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user.profile) == "testuser's Profile"

    def test_full_name_property(self):
        """Test full_name property returns correct value."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        assert user.profile.full_name == 'John Doe'

    def test_full_name_fallback_to_username(self):
        """Test full_name falls back to username when names are empty."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.profile.full_name == 'testuser'

    def test_default_max_books_allowed(self):
        """Test default max_books_allowed is 3."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.profile.max_books_allowed == 3

    def test_default_is_active_member(self):
        """Test default is_active_member is True."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.profile.is_active_member is True

    def test_can_borrow_books_when_no_loans(self):
        """Test can_borrow_books returns True when user has no active loans."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.profile.can_borrow_books() is True

    def test_can_borrow_books_when_inactive_member(self):
        """Test can_borrow_books returns False for inactive members."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.is_active_member = False
        user.profile.save()
        assert user.profile.can_borrow_books() is False
