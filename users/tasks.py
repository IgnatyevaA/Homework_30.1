"""
Периодические задачи приложения users.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей (is_active=False), которые не заходили более месяца.
    Проверка по полю last_login. Запускается по расписанию celery-beat (ежедневно).
    """
    from .models import User

    threshold = timezone.now() - timedelta(days=30)
    # Пользователи без last_login (никогда не входили) не блокируем — только по явному last_login
    updated = User.objects.filter(
        last_login__isnull=False,
        last_login__lt=threshold,
        is_active=True,
    ).update(is_active=False)
    return updated
