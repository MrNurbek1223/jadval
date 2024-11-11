from rest_framework import serializers

class AttendanceStatisticsSerializer(serializers.Serializer):
    subject = serializers.CharField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()



