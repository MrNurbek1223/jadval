from rest_framework.permissions import IsAuthenticated
from api.attendancestatistics.filters import AttendanceFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.attendance.models import Attendance


class AttendanceStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        filterset = AttendanceFilter(request.query_params, queryset=Attendance.objects.select_related('student', 'schedule'))

        if not filterset.is_valid():
            return Response({"error": filterset.errors}, status=400)

        if user.role == 'teacher':
            data = filterset.qs.filter(schedule__teacher=user, status='absent')
        elif user.role == 'student':
            data = filterset.qs.filter(student=user, status='absent')
        else:
            return Response({"error": "Sizga bu ma'lumotni ko'rish ruxsat etilmagan."}, status=403)

        response_data = [
            {
                "Fan": attendance.schedule.subject.name,
                "Sana": attendance.schedule.start_time.strftime("%Y-%m-%d %H:%M"),
                "Talaba": attendance.student.username if user.role == 'teacher' else None,
                "Holat": attendance.status,
                "Sabab": attendance.reason,
            }
            for attendance in data
        ]
        return Response(response_data, status=200)