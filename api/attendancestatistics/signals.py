from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.attendance.models import Attendance
from apps.attendancestatistics.models import AttendanceStatistics


@receiver(post_save, sender=Attendance)
def update_statistics(sender, instance, **kwargs):
    attendance_stat, created = AttendanceStatistics.objects.get_or_create(
        student=instance.student,
        subject=instance.schedule.subject,
        semester="2024-bahor"
    )

    # Statistikalarni yangilash
    attendance_stat.update_statistics()

