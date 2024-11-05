from rest_framework import serializers
from apps.attendancestatistics.models import AttendanceStatistics


class AttendanceStatisticsSerializer(serializers.ModelSerializer):
    monthly_statistics = serializers.SerializerMethodField()
    weekly_statistics = serializers.SerializerMethodField()
    daily_statistics = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceStatistics
        fields = ['student', 'subject', 'semester', 'total_classes', 'attended_classes', 'monthly_statistics', 'weekly_statistics', 'daily_statistics']

    def get_monthly_statistics(self, obj):
        return obj.calculate_monthly_statistics()

    def get_weekly_statistics(self, obj):
        return obj.calculate_weekly_statistics()

    def get_daily_statistics(self, obj):
        return obj.calculate_daily_statistics()