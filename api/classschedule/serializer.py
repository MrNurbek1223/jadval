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
    day_of_week = serializers.SerializerMethodField()  # Convert day_of_week to readable format
    subject = serializers.CharField(source='subject.name')  # Display subject name
    teacher = serializers.CharField(source='teacher.username')  # Display teacher's username
    room = serializers.CharField(source='room.name')  # Display room name
    group = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')  # Display group names

    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'group', 'day_of_week', 'start_time', 'end_time',
            'subject', 'teacher', 'room', 'session_number'
        ]
        read_only_fields = ['id']

    def get_day_of_week(self, obj):
        # Convert integer to weekday name
        days = {
            1: 'Dushanba', 2: 'Seshanba', 3: 'Chorshanba',
            4: 'Payshanba', 5: 'Juma', 6: 'Shanba'
        }
        return days.get(obj.day_of_week, "Unknown Day")