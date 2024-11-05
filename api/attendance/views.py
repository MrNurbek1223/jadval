from datetime import timedelta
from django.template.defaulttags import now
from rest_framework import viewsets
from api.attendance.serializer import AttendanceSerializer
from api.user.permission import IsTeacherUser
from apps.attendance.models import Attendance
from rest_framework import serializers
from django.utils import timezone

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return Attendance.objects.filter(schedule__teacher=self.request.user)
        elif self.request.user.role == 'admin':
            return Attendance.objects.all()
        return Attendance.objects.none()

    def perform_create(self, serializer):
        schedule = serializer.validated_data['schedule']
        if self.request.user.role == 'teacher' and (timezone.now() - schedule.start_time <= timedelta(hours=24)):
            serializer.save()
        else:
            raise serializers.ValidationError("Attendance can only be marked within 24 hours by a teacher.")