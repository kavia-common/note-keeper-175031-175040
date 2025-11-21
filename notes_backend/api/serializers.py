from rest_framework import serializers
from .models import Note

# PUBLIC_INTERFACE
class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model with validation and read-only fields."""

    class Meta:
        model = Note
        fields = ["id", "title", "content", "is_archived", "tags", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_title(self, value: str) -> str:
        """
        Ensure title is non-empty and within max length.
        """
        if value is None:
            raise serializers.ValidationError("Title is required.")
        title_str = str(value).strip()
        if title_str == "":
            raise serializers.ValidationError("Title cannot be blank.")
        if len(title_str) > 200:
            raise serializers.ValidationError("Title must be at most 200 characters.")
        return title_str
