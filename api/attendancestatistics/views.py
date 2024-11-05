from rest_framework import viewsets
from rest_framework.response import Response
from api.attendancestatistics.pagination import AttendanceStatisticsPagination
from api.attendancestatistics.serializer import AttendanceStatisticsSerializer
from api.user.permission import IsAdminOrTeacherOrReadOnly
from apps.attendancestatistics.models import AttendanceStatistics


class AttendanceStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttendanceStatistics.objects.all()
    serializer_class = AttendanceStatisticsSerializer
    pagination_class = AttendanceStatisticsPagination
    permission_classes = [IsAdminOrTeacherOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'teacher']:
            return AttendanceStatistics.objects.all()
        elif user.role == 'student':
            return AttendanceStatistics.objects.filter(student=user)
        return AttendanceStatistics.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)