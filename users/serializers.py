from rest_framework import serializers
from .models import User, Payment
from .services import (
    get_stripe_api_key,
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
)


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment. При payment_method=stripe создаёт сессию Stripe и возвращает ссылку на оплату."""
    payment_link = serializers.URLField(read_only=True, required=False)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, attrs):
        if attrs.get('payment_method') == 'stripe':
            if not attrs.get('paid_course') and not attrs.get('paid_lesson'):
                raise serializers.ValidationError(
                    'Для оплаты через Stripe укажите paid_course или paid_lesson.'
                )
            if not get_stripe_api_key():
                raise serializers.ValidationError(
                    'Оплата через Stripe недоступна: не настроен STRIPE_SECRET_KEY.'
                )
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        payment_method = validated_data.get('payment_method')
        amount = validated_data.get('amount')
        paid_course = validated_data.get('paid_course')
        paid_lesson = validated_data.get('paid_lesson')

        payment = Payment.objects.create(**validated_data)

        if payment_method == 'stripe':
            product_name = None
            if paid_course:
                product_name = paid_course.title
            elif paid_lesson:
                product_name = paid_lesson.title
            if not product_name:
                product_name = f'Payment #{payment.id}'

            amount_cents = int(amount * 100)
            request = self.context.get('request')
            base_url = request.build_absolute_uri('/') if request else 'http://localhost:8000/'
            success_url = request.data.get('success_url') or (base_url + 'api/users/payments/?success=1')
            cancel_url = request.data.get('cancel_url') or (base_url + 'api/users/payments/?cancel=1')

            product_data = create_stripe_product(product_name)
            product_id = product_data['id']
            price_data = create_stripe_price(product_id, amount_cents)
            price_id = price_data['id']
            session_data = create_stripe_checkout_session(
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user.email if user else None,
                metadata={'payment_id': str(payment.id)},
            )
            payment.stripe_session_id = session_data['id']
            payment.stripe_payment_url = session_data.get('url')
            payment.save(update_fields=['stripe_session_id', 'stripe_payment_url'])
        return payment

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.stripe_payment_url:
            rep['payment_link'] = instance.stripe_payment_url
        return rep


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
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
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