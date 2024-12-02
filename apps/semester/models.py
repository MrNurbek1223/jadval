from django.db import models
from apps.group.models import Group


class Semester(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.group.name})"
