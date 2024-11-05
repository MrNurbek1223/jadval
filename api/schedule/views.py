from rest_framework import viewsets, permissions
from api.schedule.serializer import ClassScheduleSerializer
from api.user.permission import IsAdminUser
from apps.schedule.models import ClassSchedule



class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.user.role == 'student':
            return ClassSchedule.objects.filter(student=self.request.user)
        elif self.request.user.role == 'teacher':
            return ClassSchedule.objects.filter(teacher=self.request.user)
        return ClassSchedule.objects.all()