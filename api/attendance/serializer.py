from rest_framework import serializers
from apps.attendance.models import Attendance
from django.utils import timezone
from datetime import datetime, timedelta


class AbsentStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=[('reasoned', 'Reasoned'), ('unreasoned', 'Unreasoned')])


class AttendanceCreateSerializer(serializers.ModelSerializer):
    present_students = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    absent_students = AbsentStudentSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Attendance
        fields = ['schedule', 'present_students', 'absent_students']

    def validate(self, data):
        user = self.context['request'].user
        schedule = data.get('schedule')

        if user.role != 'teacher':
            raise serializers.ValidationError("Only teachers can mark attendance.")

        if schedule.teacher != user:
            raise serializers.ValidationError("You can only mark attendance for your own classes.")

        if Attendance.objects.filter(schedule=schedule).exists():
            raise serializers.ValidationError("Attendance has already been recorded for this class.")

        if timezone.now() > schedule.start_time + timedelta(hours=24):
            raise serializers.ValidationError("Attendance can only be marked within 24 hours of the class start time.")

        return data

    def create(self, validated_data):
        present_students = validated_data.pop('present_students', [])
        absent_students = validated_data.pop('absent_students', [])
        schedule = validated_data['schedule']

        Attendance.objects.bulk_create(
            [Attendance(student_id=student_id, schedule=schedule, status='present') for student_id in
             present_students] +
            [Attendance(student_id=absent['student_id'], schedule=schedule, status='absent', reason=absent['reason'])
             for absent in absent_students]
        )
        return validated_data



class AttendanceUpdateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(write_only=True)
    status = serializers.ChoiceField(choices=[('present', 'Present'), ('absent', 'Absent')])
    reason = serializers.ChoiceField(choices=[('reasoned', 'Reasoned'), ('unreasoned', 'Unreasoned')], allow_null=True,
                                     required=False)

    class Meta:
        model = Attendance
        fields = ['student_id', 'schedule', 'status', 'reason']

    def validate(self, data):
        schedule = data.get('schedule')
        student_id = data.get('student_id')

        try:
            attendance = Attendance.objects.get(schedule=schedule, student_id=student_id)
        except Attendance.DoesNotExist:
            raise serializers.ValidationError("Attendance record does not match the provided student ID and schedule.")

        if timezone.now() > attendance.schedule.start_time + timedelta(hours=24):
            raise serializers.ValidationError("You can only update attendance within 24 hours of the class start time.")

        if data.get('status') == 'absent' and 'reason' not in data:
            raise serializers.ValidationError("A reason is required for absent students.")

        return data

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.reason = validated_data.get('reason', instance.reason if instance.status == 'absent' else None)
        instance.save()
        return instance