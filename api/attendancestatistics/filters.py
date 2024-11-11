from django.db.models import Count
from apps.attendance.models import Attendance
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
