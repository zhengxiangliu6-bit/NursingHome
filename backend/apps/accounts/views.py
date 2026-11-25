from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.permissions import IsAdmin, IsStaff
from .models import User, Role, StaffProfile, FamilyRelation, StaffSchedule
from .serializers import (
    UserSerializer, UserCreateSerializer, RoleSerializer,
    LoginSerializer, ChangePasswordSerializer,
    StaffProfileSerializer, FamilyRelationSerializer, StaffScheduleSerializer,
)


class LoginView(generics.GenericAPIView):
    """用户登录，获取JWT Token。"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class LogoutView(generics.GenericAPIView):
    """注销登录，使Refresh Token失效。"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'detail': '已退出登录'}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    """获取/更新当前用户信息。"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """修改密码。"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': '密码修改成功'})


class UserViewSet(viewsets.ModelViewSet):
    """用户管理（管理员）。"""
    queryset = User.objects.select_related('role').all()
    permission_classes = [IsAdmin]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'phone', 'first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """角色列表。"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related('user').all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAdmin]


class FamilyRelationViewSet(viewsets.ModelViewSet):
    queryset = FamilyRelation.objects.select_related('family_user', 'resident').all()
    serializer_class = FamilyRelationSerializer
    permission_classes = [IsAdmin]


class StaffScheduleViewSet(viewsets.ModelViewSet):
    """员工排班管理。"""
    queryset = StaffSchedule.objects.select_related('staff', 'building').filter(is_deleted=False)
    serializer_class = StaffScheduleSerializer
    permission_classes = [IsStaff]
    filterset_fields = ['staff', 'date', 'building', 'is_on_leave', 'shift']

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return super().get_permissions()
