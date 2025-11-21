from django.db import models


class Note(models.Model):
    """
    Represents a user note with title, content, archived flag, tags, and timestamps.
    """
    title = models.CharField(max_length=200)  # required, non-blank by default
    content = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.title} (archived={self.is_archived})"
