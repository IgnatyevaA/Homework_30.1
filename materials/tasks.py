"""
Отложенные и периодические задачи приложения materials.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_emails(course_id: int):
    """
    Отправляет подписчикам курса письмо об обновлении материалов.
    Вызывается асинхронно при обновлении курса (или урока, если курс не обновлялся 4+ часов).
    """
    from .models import Course, Subscription

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    subscribers = Subscription.objects.filter(course=course).select_related('user')
    emails = [s.user.email for s in subscribers if s.user.email]
    if not emails:
        return

    subject = f'Обновление курса: {course.title}'
    message = (
        f'Здравствуйте!\n\n'
        f'Курс «{course.title}» был обновлён. '
        f'Зайдите на платформу, чтобы посмотреть новые материалы.\n\n'
        f'С уважением,\nКоманда платформы'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
        recipient_list=emails,
        fail_silently=True,
    )
