from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.attendance.views import AttendanceViewSet
from api.attendancestatistics.views import AttendanceStatisticsViewSet
from api.schedule.views import ClassScheduleViewSet
from api.subject.views import SubjectViewSet
from api.user.views import RegisterView, LoginView

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'schedules', ClassScheduleViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'statistics', AttendanceStatisticsViewSet)
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
