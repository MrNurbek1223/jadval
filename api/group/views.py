from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from api.group.pagination import GroupPagination
from api.group.serializer import GroupSerializer
from api.user.serializer import StudentSerializer
from apps.group.models import Group
from rest_framework.response import Response
from rest_framework.decorators import action


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = []
    pagination_class = GroupPagination

    @action(detail=True, methods=['get'], url_path='students')
    def students(self, request, pk=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = StudentSerializer(group.students.all(), many=True)
        return Response(serializer.data)






