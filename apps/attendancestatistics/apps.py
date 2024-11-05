from django.apps import AppConfig


class AttendancestatisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attendancestatistics'

    def ready(self):
        import api.attendancestatistics.signals