from django_filters import rest_framework as filters

from apps.classschedule.models import ClassSchedule


class ClassScheduleFilter(filters.FilterSet):
    min_start_time = filters.TimeFilter(field_name="start_time", lookup_expr='gte')
    max_end_time = filters.TimeFilter(field_name="end_time", lookup_expr='lte')

    class Meta:
        model = ClassSchedule
        fields = ['group', 'day_of_week', 'teacher', 'room', 'subject', 'min_start_time', 'max_end_time']
