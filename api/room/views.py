from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny

from api.room.serializer import RoomSerializer
from apps.room.models import Room


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]