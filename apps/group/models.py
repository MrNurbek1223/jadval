from django.db import models
from core.settings import AUTH_USER_MODEL

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    students = models.ManyToManyField(AUTH_USER_MODEL, limit_choices_to={'role': 'student'},
                                      related_name='student_groups')



    def __str__(self):
        return str(self.id) if self.id else "Yangi guruh (hali saqlanmagan)"