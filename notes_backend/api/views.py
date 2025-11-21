from typing import Optional

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Note
from .serializers import NoteSerializer


@api_view(['GET'])
def health(request: Request):
    """
    Health check endpoint.
    Returns a simple JSON indicating the server is up.
    """
    return Response({"message": "Server is up!"})


class NoteViewSet(viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    A ViewSet providing CRUD operations for notes.

    Supports:
    - Search on title, content, tags (?search=term)
    - Ordering by created_at, updated_at, title (?ordering=title or -created_at)
    - Filtering by archived via query param (?archived=true/false)
    """
    serializer_class = NoteSerializer
    queryset = Note.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "content", "tags"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        archived_param: Optional[str] = self.request.query_params.get("archived")
        if archived_param is not None:
            val = archived_param.lower()
            if val in {"true", "1", "yes"}:
                qs = qs.filter(is_archived=True)
            elif val in {"false", "0", "no"}:
                qs = qs.filter(is_archived=False)
        return qs
