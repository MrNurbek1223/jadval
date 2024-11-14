from rest_framework.permissions import IsAuthenticated, AllowAny
from api.classschedule.filter import ClassScheduleFilter
from api.classschedule.pagination import StandardResultsSetPagination
from api.classschedule.serializer import ClassScheduleSerializer
from apps.classschedule.models import ClassSchedule
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied


class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ClassScheduleFilter
    ordering_fields = ['day_of_week', 'start_time', 'session_number']
    search_fields = ['subject__name', 'teacher__username', 'room__name']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return super().get_queryset().order_by('start_time','day_of_week')

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionDenied("Faqat admin foydalanuvchilar yozuv qo'sha oladi.")
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionDenied("Faqat admin foydalanuvchilar yozuvni yangilay oladi.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != 'admin':
            raise PermissionDenied("Faqat admin foydalanuvchilar yozuvni o'chira oladi.")
        instance.delete()
