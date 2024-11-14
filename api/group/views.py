from rest_framework import viewsets

from api.group.pagination import GroupPagination
from api.group.serializer import GroupSerializer
from apps.group.models import Group


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = []
    pagination_class = GroupPagination
