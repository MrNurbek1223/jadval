from django.db import models
from apps.group.models import Group
from apps.room.models import Room
from apps.subject.models import Subject
from core.settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError


class ClassSchedule(models.Model):
    group = models.ManyToManyField(Group)
    day_of_week = models.PositiveSmallIntegerField(choices=[
        (1, 'Dushanba'), (2, 'Seshanba'), (3, 'Chorshanba'),
        (4, 'Payshanba'), (5, 'Juma'), (6, 'Shanba')
    ])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_schedules')
    teacher = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'},
                                related_name='teacher_class_schedules')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    session_number = models.PositiveSmallIntegerField( null=True)

    class Meta:
        unique_together = ['day_of_week', 'start_time', 'end_time', 'room']

    def __str__(self):
        return f"{self.group.all().first()} - {self.get_day_of_week_display()} - {self.start_time}-{self.end_time} - Session {self.session_number} - {self.id}"

    def clean(self):
        overlap = ClassSchedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk).exists()

        if overlap:
            raise ValidationError("Ushbu xona tanlangan vaqt oralig'ida boshqa dars uchun band.")

        prev_class = ClassSchedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            end_time=self.start_time
        ).exclude(pk=self.pk).exists()

        next_class = ClassSchedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            start_time=self.end_time
        ).exclude(pk=self.pk).exists()

        if (prev_class or next_class) and not (prev_class and next_class):
            raise ValidationError("Dars xonadagi mavjud darslar bilan ketma-ket tartibda bo'lishi kerak.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
