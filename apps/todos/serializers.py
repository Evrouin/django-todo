from rest_framework import serializers

from .models import Todo
from .utils import process_image

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB


class TodoSerializer(serializers.ModelSerializer):
    """Serializer for todo items."""

    class Meta:
        model = Todo
        fields = ["id", "title", "body", "image", "thumbnail", "completed", "deleted", "pinned", "color", "created_at", "updated_at"]
        read_only_fields = ["id", "thumbnail", "created_at", "updated_at"]

    def validate_image(self, value):
        if value and value.size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("Image must be under 5MB.")
        return value

    def create(self, validated_data):
        image = validated_data.get("image")
        if image:
            validated_data["image"], validated_data["thumbnail"] = process_image(image)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_image_name = instance.image.name if instance.image else None
        old_thumbnail_name = instance.thumbnail.name if instance.thumbnail else None
        old_image_storage = instance.image.storage if instance.image else None
        old_thumbnail_storage = instance.thumbnail.storage if instance.thumbnail else None

        if "image" in validated_data:
            image = validated_data.get("image")
            if image:
                validated_data["image"], validated_data["thumbnail"] = process_image(image)
            else:
                validated_data["thumbnail"] = None

        updated = super().update(instance, validated_data)

        if "image" in validated_data:
            new_image_name = updated.image.name if updated.image else None
            new_thumbnail_name = updated.thumbnail.name if updated.thumbnail else None

            if old_image_name and old_image_name != new_image_name and old_image_storage:
                old_image_storage.delete(old_image_name)
            if old_thumbnail_name and old_thumbnail_name != new_thumbnail_name and old_thumbnail_storage:
                old_thumbnail_storage.delete(old_thumbnail_name)

        return updated
