from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PaymentViewSet, UserRegistrationAPIView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('', include(router.urls)),
]