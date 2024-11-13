from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from api.attendance.serializer import AttendanceCreateSerializer, AttendanceUpdateSerializer
from apps.attendance.models import Attendance
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Attendance.objects.filter(schedule__teacher=user)
        elif user.role == 'admin':
            return Attendance.objects.all()
        return Attendance.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return AttendanceCreateSerializer
        return AttendanceUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        schedule = serializer.validated_data.get('schedule')

        if schedule.teacher != user:
            raise PermissionDenied("You can only record attendance for your own classes.")

        serializer.save()

    def update(self, request, *args, **kwargs):
        schedule_id = request.data.get('schedule')
        student_id = request.data.get('student_id')

        if not schedule_id or not student_id:
            return Response({"detail": "Both schedule ID and student ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Attendance.objects.get(schedule_id=schedule_id, student_id=student_id)
        except Attendance.DoesNotExist:
            return Response({"detail": "Attendance record does not match the provided student ID and schedule."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)