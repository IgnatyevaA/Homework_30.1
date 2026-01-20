from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment"""
    class Meta:
        model = Payment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_staff', 'is_active', 'date_joined', 'payments']
        read_only_fields = ['id', 'date_joined']