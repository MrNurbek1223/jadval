from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.attendancestatistics.filters import (
    get_group_subject_statistics,
    get_group_all_subjects_statistics,
    get_student_all_subjects_statistics,
    get_student_subject_statistics
)


class AttendanceStatisticsView(APIView):

    def get(self, request):
        group_id = request.query_params.get('group_id')
        subject_id = request.query_params.get('subject_id')
        student_id = request.query_params.get('student_id')
        period = request.query_params.get('period')

        if not period:
            return Response({"error": "Davr ('period') parametri kerak."}, status=status.HTTP_400_BAD_REQUEST)

        if group_id and subject_id:
            data = get_group_subject_statistics(group_id, subject_id, period)

        elif group_id and not subject_id:
            data = get_group_all_subjects_statistics(group_id, period)

        elif student_id and not subject_id:
            data = get_student_all_subjects_statistics(student_id, period)

        elif student_id and subject_id:
            data = get_student_subject_statistics(student_id, subject_id, period)

        else:
            return Response({"error": "To'g'ri parametrlarni kiriting (group_id va subject_id yoki student_id)."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)
