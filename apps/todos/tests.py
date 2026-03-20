import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image as PilImage

from .models import Todo

User = get_user_model()


def make_test_image(*, color: tuple[int, int, int], name: str) -> SimpleUploadedFile:
    """Create an in-memory image suitable for upload tests."""

    image = PilImage.new("RGB", (64, 64), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name=name, content=buffer.read(), content_type="image/png")


@pytest.fixture
def api_client():
    """API client fixture."""
    return APIClient()


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


@pytest.fixture
def auth_client(api_client, create_user):
    """Authenticated API client."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def create_todo(db):
    """Create a test todo."""

    def make_todo(user, **kwargs):
        return Todo.objects.create(
            user=user,
            title=kwargs.get("title", "Test todo"),
            body=kwargs.get("body", "Test body"),
            completed=kwargs.get("completed", False),
            deleted=kwargs.get("deleted", False),
        )

    return make_todo


@pytest.mark.django_db
class TestTodoList:
    """Test todo list endpoint."""

    def test_list_todos(self, auth_client, create_todo):
        """Test listing todos for authenticated user."""
        client, user = auth_client
        create_todo(user, title="Todo 1")
        create_todo(user, title="Todo 2")
        response = client.get("/api/todos/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 2

    def test_list_excludes_deleted(self, auth_client, create_todo):
        """Test that soft-deleted todos are excluded by default."""
        client, user = auth_client
        create_todo(user, title="Active")
        create_todo(user, title="Deleted", deleted=True)
        response = client.get("/api/todos/")
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["title"] == "Active"

    def test_list_include_deleted(self, auth_client, create_todo):
        """Test including soft-deleted todos with query param."""
        client, user = auth_client
        create_todo(user, title="Active")
        create_todo(user, title="Deleted", deleted=True)
        response = client.get("/api/todos/?include_deleted=true")
        assert len(response.data["data"]) == 2

    def test_list_only_own_todos(self, api_client, create_user, create_todo):
        """Test that users only see their own todos."""
        user1 = create_user(email="user1@example.com", username="user1")
        user2 = create_user(email="user2@example.com", username="user2")
        create_todo(user1, title="User1 todo")
        create_todo(user2, title="User2 todo")
        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/todos/")
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["title"] == "User1 todo"

    def test_list_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list todos."""
        response = api_client.get("/api/todos/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTodoCreate:
    """Test todo creation endpoint."""

    def test_create_todo(self, auth_client):
        """Test creating a todo."""
        client, user = auth_client
        response = client.post("/api/todos/", {"title": "New todo", "body": "Details"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["title"] == "New todo"
        assert Todo.objects.filter(user=user).count() == 1

    def test_create_todo_minimal(self, auth_client):
        """Test creating a todo with only title."""
        client, _ = auth_client
        response = client.post("/api/todos/", {"title": "Just a title"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["completed"] is False
        assert response.data["data"]["deleted"] is False

    def test_create_todo_no_title(self, auth_client):
        """Test creating a todo without title fails."""
        client, _ = auth_client
        response = client.post("/api/todos/", {"body": "No title"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTodoDetail:
    """Test todo detail endpoint."""

    def test_get_todo(self, auth_client, create_todo):
        """Test getting a single todo."""
        client, user = auth_client
        todo = create_todo(user)
        response = client.get(f"/api/todos/{todo.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == todo.title

    def test_get_other_user_todo(self, api_client, create_user, create_todo):
        """Test that users cannot access other users' todos."""
        user1 = create_user(email="user1@example.com", username="user1")
        user2 = create_user(email="user2@example.com", username="user2")
        todo = create_todo(user1)
        api_client.force_authenticate(user=user2)
        response = api_client.get(f"/api/todos/{todo.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_todo(self, auth_client):
        """Test getting a todo that doesn't exist."""
        client, _ = auth_client
        response = client.get("/api/todos/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTodoUpdate:
    """Test todo update endpoints."""

    def test_full_update(self, auth_client, create_todo):
        """Test full update of a todo."""
        client, user = auth_client
        todo = create_todo(user)
        response = client.put(
            f"/api/todos/{todo.id}/",
            {"title": "Updated", "body": "Updated body", "completed": True},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["title"] == "Updated"
        assert response.data["data"]["completed"] is True

    def test_partial_update(self, auth_client, create_todo):
        """Test partial update (toggle completed)."""
        client, user = auth_client
        todo = create_todo(user)
        response = client.patch(f"/api/todos/{todo.id}/", {"completed": True})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["completed"] is True
        assert response.data["data"]["title"] == todo.title

    def test_update_other_user_todo(self, api_client, create_user, create_todo):
        """Test that users cannot update other users' todos."""
        user1 = create_user(email="user1@example.com", username="user1")
        user2 = create_user(email="user2@example.com", username="user2")
        todo = create_todo(user1)
        api_client.force_authenticate(user=user2)
        response = api_client.patch(f"/api/todos/{todo.id}/", {"completed": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTodoDelete:
    """Test todo delete endpoint."""

    def test_soft_delete(self, auth_client, create_todo):
        """Test first delete soft-deletes the todo."""
        client, user = auth_client
        todo = create_todo(user)
        response = client.delete(f"/api/todos/{todo.id}/")
        assert response.status_code == status.HTTP_200_OK
        todo.refresh_from_db()
        assert todo.deleted is True

    def test_permanent_delete(self, auth_client, create_todo):
        """Test second delete permanently removes the todo."""
        client, user = auth_client
        todo = create_todo(user, deleted=True)
        response = client.delete(f"/api/todos/{todo.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert not Todo.objects.filter(id=todo.id).exists()

    def test_delete_other_user_todo(self, api_client, create_user, create_todo):
        """Test that users cannot delete other users' todos."""
        user1 = create_user(email="user1@example.com", username="user1")
        user2 = create_user(email="user2@example.com", username="user2")
        todo = create_todo(user1)
        api_client.force_authenticate(user=user2)
        response = api_client.delete(f"/api/todos/{todo.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTodoImageStorageCleanup:
    """Test file cleanup on image replacement and permanent deletion."""

    def test_replacing_image_deletes_old_files(self, auth_client, tmp_path):
        client, user = auth_client
        image1 = make_test_image(color=(255, 0, 0), name="image1.png")
        image2 = make_test_image(color=(0, 255, 0), name="image2.png")

        with override_settings(
            MEDIA_ROOT=tmp_path,
            STORAGES={
                "default": {
                    "BACKEND": "django.core.files.storage.FileSystemStorage",
                    "OPTIONS": {"location": str(tmp_path)},
                },
                "staticfiles": {
                    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                },
            },
        ):
            response = client.post(
                "/api/todos/",
                {"title": "Todo with image", "body": "Details", "image": image1},
                format="multipart",
            )
            assert response.status_code == status.HTTP_201_CREATED

            todo = Todo.objects.get(id=response.data["data"]["id"])
            old_image_name = todo.image.name
            old_thumbnail_name = todo.thumbnail.name
            assert (tmp_path / old_image_name).exists()
            assert (tmp_path / old_thumbnail_name).exists()

            response = client.put(
                f"/api/todos/{todo.id}/",
                {"title": "Replaced", "body": "New body", "image": image2},
                format="multipart",
            )
            assert response.status_code == status.HTTP_200_OK

            todo.refresh_from_db()
            new_image_name = todo.image.name
            new_thumbnail_name = todo.thumbnail.name
            assert (tmp_path / new_image_name).exists()
            assert (tmp_path / new_thumbnail_name).exists()

            # Old objects should be removed from storage.
            assert not (tmp_path / old_image_name).exists()
            assert not (tmp_path / old_thumbnail_name).exists()

    def test_permanent_delete_removes_files(self, auth_client, tmp_path):
        client, user = auth_client
        image = make_test_image(color=(0, 0, 255), name="image.png")

        with override_settings(
            MEDIA_ROOT=tmp_path,
            STORAGES={
                "default": {
                    "BACKEND": "django.core.files.storage.FileSystemStorage",
                    "OPTIONS": {"location": str(tmp_path)},
                },
                "staticfiles": {
                    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                },
            },
        ):
            response = client.post(
                "/api/todos/",
                {"title": "Todo to delete", "body": "Details", "image": image},
                format="multipart",
            )
            assert response.status_code == status.HTTP_201_CREATED

            todo = Todo.objects.get(id=response.data["data"]["id"])
            old_image_name = todo.image.name
            old_thumbnail_name = todo.thumbnail.name
            assert (tmp_path / old_image_name).exists()
            assert (tmp_path / old_thumbnail_name).exists()

            # First delete is a soft delete: files must remain.
            response = client.delete(f"/api/todos/{todo.id}/")
            assert response.status_code == status.HTTP_200_OK
            todo.refresh_from_db()
            assert todo.deleted is True
            assert (tmp_path / old_image_name).exists()
            assert (tmp_path / old_thumbnail_name).exists()

            # Second delete is permanent: files must be removed.
            response = client.delete(f"/api/todos/{todo.id}/")
            assert response.status_code == status.HTTP_200_OK
            assert not Todo.objects.filter(id=todo.id).exists()
            assert not (tmp_path / old_image_name).exists()
            assert not (tmp_path / old_thumbnail_name).exists()


@pytest.mark.django_db
class TestApiResponseFormat:
    """Test that responses follow the ApiResponse format."""

    def test_response_format(self, auth_client, create_todo):
        """Test response contains data, statusCode, and timestamp."""
        client, user = auth_client
        create_todo(user)
        response = client.get("/api/todos/")
        assert "data" in response.data
        assert "statusCode" in response.data
        assert "timestamp" in response.data
