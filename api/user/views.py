from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.user.pagination import UserPagination
from api.user.serializer import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer, TeacherSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from apps.user.models import User


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),

            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(role='teacher')
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]
    pagination_class = UserPagination