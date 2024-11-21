from rest_framework import serializers
from apps.classschedule.models import ClassSchedule


class ClassScheduleSerializer1(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'group', 'day_of_week', 'start_time', 'end_time',
            'subject', 'teacher', 'room', 'session_number'
        ]
        read_only_fields = ['id']




class ClassScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    day_of_week = serializers.SerializerMethodField()
    subject = serializers.CharField(source='subject.name')
    teacher = serializers.CharField(source='teacher.username')
    room = serializers.CharField(source='room.name')
    room_number = serializers.CharField(source='room.number')
    group = serializers.SerializerMethodField()

    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'group', 'day_of_week', 'start_time', 'end_time',
            'subject', 'teacher', 'room', 'room_number', 'session_number'
        ]
        read_only_fields = ['id']

    def get_day_of_week(self, obj):
        days = {
            1: 'Dushanba', 2: 'Seshanba', 3: 'Chorshanba',
            4: 'Payshanba', 5: 'Juma', 6: 'Shanba'
        }
        return days.get(obj.day_of_week, "Unknown Day")

    def get_group(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.group.all()]
