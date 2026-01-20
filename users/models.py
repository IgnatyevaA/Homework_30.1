from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('transfer', _('Transfer')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name=_('user'))
    payment_date = models.DateTimeField(_('payment date'), auto_now_add=True)
    paid_course = models.ForeignKey('materials.Course', on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='payments', verbose_name=_('paid course'))
    paid_lesson = models.ForeignKey('materials.Lesson', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='payments', verbose_name=_('paid lesson'))
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('payment method'), max_length=10, choices=PAYMENT_METHOD_CHOICES)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.user.email} - {self.amount} ({self.payment_date})"
