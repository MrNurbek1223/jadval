from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.attendancestatistics.utils import get_student_attendance_statistics


class AttendanceStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        stats = get_student_attendance_statistics(student_id)
        return Response(stats)