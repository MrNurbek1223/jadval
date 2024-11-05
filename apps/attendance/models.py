from django.db import models
from apps.schedule.models import ClassSchedule
from apps.user.models import User



class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    reason = models.CharField(max_length=10, choices=[('excused', 'Excused'), ('unexcused', 'Unexcused')], null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}- {self.schedule} - {self.status} -id- {self.id}"