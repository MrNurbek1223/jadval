from rest_framework import serializers

from apps.schedule.models import ClassSchedule


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = ['id', 'subject', 'teacher', 'start_time', 'end_time']