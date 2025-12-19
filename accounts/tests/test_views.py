import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User


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


@pytest.mark.django_db
class TestRegisterView:
    """Tests for user registration endpoint."""

    def test_register_success(self, api_client):
        """Test successful user registration."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_register_invalid_data(self, api_client):
        """Test registration with invalid data."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'pass',
            'password_confirm': 'pass'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginView:
    """Tests for user login endpoint."""

    def test_login_success(self, api_client, user):
        """Test successful login."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, api_client, user):
        """Test login with wrong password."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileView:
    """Tests for user profile endpoint."""

    def test_get_profile_authenticated(self, api_client, user):
        """Test getting profile when authenticated."""
        api_client.force_authenticate(user=user)
        url = reverse('profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'phone_number' in response.data

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile without authentication."""
        url = reverse('profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, api_client, user):
        """Test updating profile."""
        api_client.force_authenticate(user=user)
        url = reverse('profile')
        data = {'phone_number': '9876543210'}
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == '9876543210'


@pytest.mark.django_db
class TestUserViewSet:
    """Tests for admin user management endpoint."""

    def test_list_users_as_admin(self, api_client, admin_user, user):
        """Test admin can list users."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2

    def test_list_users_as_regular_user(self, api_client, user):
        """Test regular user cannot list users."""
        api_client.force_authenticate(user=user)
        url = reverse('user-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthenticated(self, api_client):
        """Test unauthenticated user cannot list users."""
        url = reverse('user-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
