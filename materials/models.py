from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    """Модель курса"""
    title = models.CharField(_('title'), max_length=200)
    preview = models.ImageField(_('preview'), upload_to='courses/', blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='courses', verbose_name=_('owner'))
    updated_at = models.DateTimeField(_('updated at'), auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока, связанная с курсом"""
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    preview = models.ImageField(_('preview'), upload_to='lessons/', blank=True, null=True)
    video_url = models.URLField(_('video URL'), blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('course'))
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True,
                           related_name='lessons', verbose_name=_('owner'))

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """Подписка пользователя на обновления курса"""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='course_subscriptions',
        verbose_name=_('user'),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('course'),
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_subscription'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.course}'