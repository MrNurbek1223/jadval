from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from api.subject.pagination import SubjectPagination
from api.subject.serializer import SubjectSerializer
from apps.subject.models import Subject
from rest_framework.filters import SearchFilter


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    pagination_class = SubjectPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']