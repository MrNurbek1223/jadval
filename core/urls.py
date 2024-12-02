from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.attendance.views import AttendanceViewSet
from api.attendancestatistics.views import AttendanceStatisticsView, GroupSubjectStatisticsView
from api.classschedule.views import ClassScheduleViewSet, TeacherClassScheduleViewSet
from api.group.views import GroupViewSet, ClassScheduleGroupsAPIView
from api.room.views import RoomViewSet
from api.subject.views import SubjectViewSet
from api.user.views import RegisterView, LoginView, TeacherViewSet

router = DefaultRouter()
router.register(r'subject', SubjectViewSet)
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'schedules', ClassScheduleViewSet, basename='classschedule')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'teacher/schedules', TeacherClassScheduleViewSet, basename='teacher-schedules')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('attendance-statistics/', AttendanceStatisticsView.as_view(), name='attendance_statistics'),
    path('', include(router.urls)),
    path('schedule/<int:class_schedule_id>/groups/', ClassScheduleGroupsAPIView.as_view(),
         name='schedule-groups'),
    path('group-subject-statistics/', GroupSubjectStatisticsView.as_view(), name='group-subject-statistics'),
]
