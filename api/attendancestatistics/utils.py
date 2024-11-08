from datetime import timedelta
from django.utils import timezone
from apps.attendance.models import Attendance


def get_student_attendance_statistics(student_id, schedule_id=None):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    daily_attendance = Attendance.objects.filter(
        student_id=student_id,
        timestamp__date=today
    ).count()

    weekly_attendance = Attendance.objects.filter(
        student_id=student_id,
        timestamp__date__gte=week_start
    ).count()

    monthly_attendance = Attendance.objects.filter(
        student_id=student_id,
        timestamp__date__gte=month_start
    ).count()

    return {
        "daily_attendance": daily_attendance,
        "weekly_attendance": weekly_attendance,
        "monthly_attendance": monthly_attendance,
    }
