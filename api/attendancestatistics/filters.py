from django.db.models import Count
from apps.attendance.models import Attendance
from apps.classschedule.models import ClassSchedule
from .utils import get_date_range


def get_group_subject_statistics(group_id, subject_id, period):
    start_date, end_date = get_date_range(period)
    attendance_data = Attendance.objects.filter(
        student__student_groups__id=group_id,
        schedule__subject_id=subject_id,
        timestamp__range=[start_date, end_date]
    ).values('status').annotate(count=Count('status'))

    return {entry['status']: entry['count'] for entry in attendance_data}


def get_group_all_subjects_statistics(group_id, period):
    start_date, end_date = get_date_range(period)
    attendance_data = Attendance.objects.filter(
        student__student_groups__id=group_id,
        timestamp__range=[start_date, end_date]
    ).values('schedule__subject__name', 'status').annotate(count=Count('status'))

    data = {}
    for entry in attendance_data:
        subject = entry['schedule__subject__name']
        if subject not in data:
            data[subject] = {}
        data[subject][entry['status']] = entry['count']
    return data


def get_student_all_subjects_statistics(student_id, period):
    start_date, end_date = get_date_range(period)
    attendance_data = Attendance.objects.filter(
        student_id=student_id,
        timestamp__range=[start_date, end_date]
    ).values('schedule__subject__name', 'status').annotate(count=Count('status'))

    data = {}
    for entry in attendance_data:
        subject = entry['schedule__subject__name']
        if subject not in data:
            data[subject] = {}
        data[subject][entry['status']] = entry['count']
    return data


def get_student_subject_statistics(student_id, subject_id, period):
    start_date, end_date = get_date_range(period)
    attendance_data = Attendance.objects.filter(
        student_id=student_id,
        schedule__subject_id=subject_id,
        timestamp__range=[start_date, end_date]
    ).values('status').annotate(count=Count('status'))

    return {entry['status']: entry['count'] for entry in attendance_data}



from apps.attendance.models import Attendance




def filter_teacher_attendance(user, group_id=None, subject_id=None):
    """
    O'qituvchiga tegishli guruh va fan bo'yicha davomatni filtrlash.
    """
    if group_id and subject_id:
        schedules = ClassSchedule.objects.filter(teacher=user, group__id=group_id, subject_id=subject_id)
    elif group_id:
        schedules = ClassSchedule.objects.filter(teacher=user, group__id=group_id)
    elif subject_id:
        schedules = ClassSchedule.objects.filter(teacher=user, subject_id=subject_id)
    else:
        return None

    return Attendance.objects.filter(schedule__in=schedules).values(
        'timestamp', 'schedule__subject__name', 'student__username', 'status', 'reason'
    ).order_by('timestamp')


def filter_student_attendance(user, subject_id):
    """
    Talabaning o'zi qoldirgan darslarini fan bo'yicha filtrlash.
    """
    return Attendance.objects.filter(
        student=user,
        schedule__subject_id=subject_id
    ).values(
        'timestamp', 'schedule__subject__name', 'status', 'reason'
    ).order_by('timestamp')
import django_filters


class AttendanceFilter(django_filters.FilterSet):
    group_id = django_filters.NumberFilter(field_name="group__id")
    subject_id = django_filters.NumberFilter(field_name="schedule__subject__id")

    class Meta:
        model = Attendance
        fields = ['group_id', 'subject_id', 'status']