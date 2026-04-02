from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.notes.models import Note

User = get_user_model()


class AdminNoteSerializer(serializers.ModelSerializer):
    """Note serializer with user info for admin views."""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "body",
            "image",
            "completed",
            "deleted",
            "pinned",
            "user_email",
            "username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates (allows is_active, is_verified, is_superuser)."""

    class Meta:
        model = User
        fields = ["username", "email", "phone", "bio", "is_active", "is_verified", "is_superuser"]


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Serializer for admin user creation."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "username", "password", "is_active", "is_superuser", "is_verified"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
