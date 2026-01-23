from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer, UserPublicSerializer
from .permissions import IsOwnerOrReadOnly


class UserRegistrationAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями (CRUD)"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'retrieve':
            # Проверяем, просматривает ли пользователь свой профиль
            pk = self.kwargs.get('pk')
            if pk and str(pk) != str(self.request.user.id):
                # Для просмотра чужого профиля используем публичный сериализатор
                return UserPublicSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Разграничение прав доступа по action"""
        if self.action == 'create':
            # Создание через регистрацию (AllowAny)
            permission_classes = [AllowAny]
        else:
            # Остальные действия требуют авторизации
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с платежами (CRUD) с фильтрацией"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']