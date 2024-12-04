from rest_framework.permissions import IsAuthenticated
from api.attendancestatistics.filters import AttendanceFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.attendance.models import Attendance
from apps.classschedule.models import ClassSchedule
from apps.group.models import Group
from django.db.models import Count, Q

from apps.semester.models import Semester


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




class GroupSubjectStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        role = user.role
        group_id = request.query_params.get('group_id', None)

        if not group_id:
            return Response({"detail": "Guruh ID sini ko'rsatish kerak."}, status=400)

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"detail": "Guruh topilmadi."}, status=404)

        if role == 'teacher' and not ClassSchedule.objects.filter(group=group, teacher=user).exists():
            return Response({"detail": "Siz bu guruhga bog'liq emassiz."}, status=403)

        if role not in ['admin', 'teacher']:
            return Response({"detail": "Siz bu ma'lumotga ruxsatga ega emassiz."}, status=403)

        semesters = Semester.objects.filter(group=group)

        semester_stats = []
        for semester in semesters:
            subjects = ClassSchedule.objects.filter(
                group=group,
                start_time__date__gte=semester.start_date,
                end_time__date__lte=semester.end_date
            ).values('subject__name').annotate(
                total_classes=Count('id'),
                total_present=Count('attendances', filter=Q(attendances__status='present')),
                total_absent=Count('attendances', filter=Q(attendances__status='absent')),
                reasoned_absences=Count('attendances', filter=Q(attendances__status='absent', attendances__reason='reasoned')),
                unreasoned_absences=Count('attendances', filter=Q(attendances__status='absent', attendances__reason='unreasoned'))
            )
            semester_stats.append({
                "semester_name": semester.name,
                "start_date": semester.start_date,
                "end_date": semester.end_date,
                "subjects": list(subjects)
            })
        data = {
            "group_name": group.name,
            "semesters": semester_stats
        }

        return Response(data)
