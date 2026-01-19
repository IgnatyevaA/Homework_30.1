from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    """Модель курса"""
    title = models.CharField(_('title'), max_length=200)
    preview = models.ImageField(_('preview'), upload_to='courses/', blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)

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

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')

    def __str__(self):
        return self.title