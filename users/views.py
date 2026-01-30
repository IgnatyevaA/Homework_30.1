from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer, UserPublicSerializer
from .permissions import IsOwnerOrReadOnly
from .services import retrieve_stripe_checkout_session


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
    """ViewSet для работы с платежами (CRUD) с фильтрацией. При payment_method=stripe возвращает payment_link."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        """Пользователь видит только свои платежи."""
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentStatusAPIView(APIView):
    """
    Проверка статуса платежа Stripe по id сессии (Session Retrieve).
    GET /api/users/payments/status/?session_id=cs_xxx
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('session_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Stripe Checkout Session ID'),
        ],
        responses={
            200: openapi.Response(
                description='Статус платежа',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'stripe_session_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'payment_status': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            404: 'Платёж не найден',
            502: 'Ошибка Stripe API',
        },
    )
    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'Укажите session_id в query-параметрах.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = Payment.objects.filter(
            user=request.user,
            stripe_session_id=session_id,
        ).first()
        if not payment:
            return Response(
                {'error': 'Платёж не найден или доступ запрещён.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        session_data = retrieve_stripe_checkout_session(session_id)
        if not session_data:
            return Response(
                {'error': 'Не удалось получить данные сессии Stripe.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({
            'payment_id': payment.id,
            'stripe_session_id': session_data.get('id'),
            'payment_status': session_data.get('payment_status'),
            'status': session_data.get('status'),
        })