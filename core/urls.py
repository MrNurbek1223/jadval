from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.attendance.views import AttendanceViewSet
from api.attendancestatistics.views import AttendanceStatisticsView
from api.classschedule.views import ClassScheduleViewSet
from api.group.views import GroupViewSet
from api.room.views import RoomViewSet
from api.subject.views import SubjectViewSet
from api.user.views import RegisterView, LoginView, TeacherViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'schedules', ClassScheduleViewSet, basename='classschedule')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'rooms', RoomViewSet, basename='room')
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('attendance-statistics/', AttendanceStatisticsView.as_view(), name='attendance_statistics'),
    path('', include(router.urls)),
]
