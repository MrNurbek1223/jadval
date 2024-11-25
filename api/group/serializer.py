from rest_framework import serializers

from api.user.serializer import StudentSerializer
from apps.group.models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']



class GroupSerializerS(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'students']