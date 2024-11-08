from rest_framework import serializers

from apps.classschedule.models import ClassSchedule


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'group', 'day_of_week', 'start_time', 'end_time',
            'subject', 'teacher', 'room', 'session_number'
        ]
        read_only_fields = ['id']