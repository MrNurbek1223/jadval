from django.db import models
from apps.attendance.models import Attendance
from apps.subject.models import Subject
from apps.user.models import User
from django.utils import timezone
from datetime import timedelta


class AttendanceStatistics(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    total_classes = models.PositiveIntegerField(default=0)  # Dastlabki qiymat
    attended_classes = models.PositiveIntegerField(default=0)  # Dastlabki qiymat
    monthly_statistics = models.JSONField(blank=True, null=True)
    weekly_statistics = models.JSONField(blank=True, null=True)
    daily_statistics = models.JSONField(blank=True, null=True)

    def calculate_monthly_statistics(self):
        stats = Attendance.objects.filter(
            student=self.student,
            schedule__subject=self.subject,
            timestamp__year=timezone.now().year,
            status='present'
        )

        monthly_data = {}
        for attendance in stats:
            month = attendance.timestamp.strftime("%Y-%m")
            monthly_data[month] = monthly_data.get(month, 0) + 1
        return monthly_data

    def calculate_weekly_statistics(self):
        last_week = timezone.now() - timedelta(days=7)
        weekly_count = Attendance.objects.filter(
            student=self.student,
            schedule__subject=self.subject,
            timestamp__gte=last_week,
            status='present'
        ).count()
        return weekly_count

    def calculate_daily_statistics(self):
        today = timezone.now().date()
        daily_count = Attendance.objects.filter(
            student=self.student,
            schedule__subject=self.subject,
            timestamp__date=today,
            status='present'
        ).count()
        return daily_count

    def update_statistics(self):
        self.total_classes = Attendance.objects.filter(
            schedule__subject=self.subject
        ).count()
        self.attended_classes = Attendance.objects.filter(
            schedule__subject=self.subject,
            status="present"
        ).count()
        self.monthly_statistics = self.calculate_monthly_statistics()
        self.weekly_statistics = self.calculate_weekly_statistics()
        self.daily_statistics = self.calculate_daily_statistics()
        self.save()