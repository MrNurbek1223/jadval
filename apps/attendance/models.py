from django.db import models
from apps.classschedule.models import ClassSchedule
from core.settings import AUTH_USER_MODEL


class Attendance(models.Model):
    student = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    reason = models.CharField(max_length=10, choices=[('reasoned', 'Sababli'), ('unreasoned', 'Sababsiz')], blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'schedule']

    def __str__(self):
        return f"{self.student} - {self.schedule} - {self.status} -id- {self.id}"