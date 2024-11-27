from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from api.group.pagination import GroupPagination
from api.group.serializer import GroupSerializer, GroupSerializerS
from api.user.serializer import StudentSerializer
from apps.classschedule.models import ClassSchedule
from apps.group.models import Group
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = []
    pagination_class = GroupPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'], url_path='students')
    def students(self, request, pk=None):
        group = get_object_or_404(Group, pk=pk)
        serializer = StudentSerializer(group.students.all(), many=True)
        return Response(serializer.data)



class ClassScheduleGroupsAPIView(APIView):
    def get(self, request, class_schedule_id):
        try:
            class_schedule = ClassSchedule.objects.get(id=class_schedule_id)
        except ClassSchedule.DoesNotExist:
            raise NotFound("Dars jadvali topilmadi.")

        groups = class_schedule.group.all()
        serializer = GroupSerializerS(groups, many=True)
        return Response(serializer.data)

