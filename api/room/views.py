from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from api.room.pagination import RoomPagination
from api.room.serializer import RoomSerializer
from apps.room.models import Room


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    pagination_class = RoomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']