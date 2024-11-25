from rest_framework import serializers
from apps.attendance.models import Attendance
from django.utils import timezone
from datetime import datetime, timedelta

from apps.group.models import Group


class AbsentStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    reason = serializers.ChoiceField(choices=[('reasoned', 'Reasoned'), ('unreasoned', 'Unreasoned')])


from rest_framework.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

class AttendanceCreateSerializer(serializers.ModelSerializer):
    absent_students = AbsentStudentSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Attendance
        fields = ['schedule', 'group', 'absent_students']

    def validate(self, data):
        user = self.context['request'].user
        schedule = data.get('schedule')
        group = data.get('group')

        if user.role != 'teacher':
            raise ValidationError("Only teachers can mark attendance.")

        if schedule.teacher != user:
            raise ValidationError("You can only mark attendance for your own classes.")

        if Attendance.objects.filter(schedule=schedule).exists():
            raise ValidationError("Attendance has already been recorded for this class.")

        if timezone.now() > schedule.start_time + timedelta(hours=24):
            raise ValidationError("Attendance can only be marked within 24 hours of the class start time.")

        return data

    def create(self, validated_data):
        schedule = validated_data['schedule']
        group_id = self.context['request'].data.get('group')
        absent_students_data = validated_data.pop('absent_students', [])

        if not group_id:
            raise ValidationError("Group ID is required.")

        # Fetch all students in the group
        group_students = Group.objects.get(id=group_id).students.values_list('id', flat=True)

        absent_students = {absent['student_id']: absent['reason'] for absent in absent_students_data}

        attendances = []
        for student_id in group_students:
            if student_id in absent_students:
                attendances.append(
                    Attendance(
                        student_id=student_id,
                        schedule=schedule,
                        status='absent',
                        reason=absent_students[student_id]
                    )
                )
            else:
                attendances.append(
                    Attendance(
                        student_id=student_id,
                        schedule=schedule,
                        status='present'
                    )
                )

        Attendance.objects.bulk_create(attendances)
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