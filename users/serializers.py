from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment"""
    class Meta:
        model = Payment
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'city']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_staff', 'is_active', 'date_joined', 'payments']
        read_only_fields = ['id', 'date_joined']


class UserPublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного просмотра профиля (без пароля, фамилии и платежей)"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone', 'city', 'avatar', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']