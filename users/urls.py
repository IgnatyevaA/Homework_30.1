from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PaymentViewSet, UserRegistrationAPIView, PaymentStatusAPIView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('payments/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('', include(router.urls)),
]