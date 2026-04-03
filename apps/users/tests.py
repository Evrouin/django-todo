import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


@pytest.fixture
def user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!",
        "password2": "SecurePass123!",
    }


@pytest.fixture
def create_user(db):
    """Create a test user."""

    def make_user(**kwargs):
        return User.objects.create_user(
            email=kwargs.get("email", "user@example.com"),
            username=kwargs.get("username", "testuser"),
            password=kwargs.get("password", "SecurePass123!"),
        )

    return make_user


@pytest.mark.django_db
class TestRegistration:
    """Test user registration."""

    def test_register_success(self, api_client, user_data):
        """Test successful user registration."""
        response = api_client.post("/api/auth/register/", user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert User.objects.filter(email=user_data["email"]).exists()

    def test_register_duplicate_email(self, api_client, user_data, create_user):
        """Test registration with duplicate email."""
        create_user(email=user_data["email"])
        response = api_client.post("/api/auth/register/", user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client, user_data):
        """Test registration with mismatched passwords."""
        user_data["password2"] = "DifferentPass123!"
        response = api_client.post("/api/auth/register/", user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client, user_data):
        """Test registration with weak password."""
        user_data["password"] = "123"
        user_data["password2"] = "123"
        response = api_client.post("/api/auth/register/", user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints."""

    def test_login_success(self, api_client, create_user):
        """Test successful login."""
        user = create_user(email="test@example.com", password="SecurePass123!")
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        response = api_client.post(
            "/api/auth/login/", {"email": "test@example.com", "password": "SecurePass123!"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client, create_user):
        """Test login with invalid credentials."""
        user = create_user(email="test@example.com")
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        response = api_client.post(
            "/api/auth/login/", {"email": "test@example.com", "password": "WrongPassword123!"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, create_user):
        """Test token refresh."""
        user = create_user(email="test@example.com", password="SecurePass123!")
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        login_response = api_client.post(
            "/api/auth/login/", {"email": "test@example.com", "password": "SecurePass123!"}
        )
        refresh_token = login_response.data["refresh"]

        response = api_client.post("/api/auth/token/refresh/", {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_profile(self, api_client, create_user):
        """Test getting user profile."""
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_update_profile(self, api_client, create_user):
        """Test updating user profile."""
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            "/api/auth/profile/", {"bio": "Updated bio", "phone": "+1234567890"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Updated bio"

    def test_profile_unauthenticated(self, api_client):
        """Test profile access without authentication."""
        response = api_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordManagement:
    """Test password change and reset."""

    def test_change_password_success(self, api_client, create_user):
        """Test successful password change."""
        user = create_user(password="OldPass123!")
        api_client.force_authenticate(user=user)
        response = api_client.put(
            "/api/auth/change-password/",
            {
                "old_password": "OldPass123!",
                "new_password": "NewPass123!",
                "new_password2": "NewPass123!",
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old(self, api_client, create_user):
        """Test password change with wrong old password."""
        user = create_user(password="OldPass123!")
        api_client.force_authenticate(user=user)
        response = api_client.put(
            "/api/auth/change-password/",
            {
                "old_password": "WrongPass123!",
                "new_password": "NewPass123!",
                "new_password2": "NewPass123!",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_request(self, api_client, create_user):
        """Test password reset request."""
        create_user(email="test@example.com")
        response = api_client.post("/api/auth/password-reset/", {"email": "test@example.com"})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestEmailVerification:
    """Test email verification."""

    def test_verify_email_success(self, api_client, create_user):
        """Test successful email verification."""
        user = create_user()
        user.generate_verification_token()
        token = user.verification_token

        response = api_client.post(f"/api/auth/verify-email/{token}/")
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.is_verified is True

    def test_verify_email_invalid_token(self, api_client):
        """Test email verification with invalid token."""
        response = api_client.post("/api/auth/verify-email/invalid-token/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
