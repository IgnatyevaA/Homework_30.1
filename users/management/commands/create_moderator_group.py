from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группу модераторов с необходимыми правами'

    def handle(self, *args, **options):
        # Создаем или получаем группу модераторов
        group, created = Group.objects.get_or_create(name='moderators')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Группа модераторов создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа модераторов уже существует.'))

        # Получаем ContentType для моделей Course и Lesson
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Получаем права для курсов и уроков
        course_permissions = Permission.objects.filter(content_type=course_content_type)
        lesson_permissions = Permission.objects.filter(content_type=lesson_content_type)

        # Добавляем права на просмотр и изменение (но не создание и удаление)
        permissions_to_add = []
        
        # Права для курсов: view, change (но не add, delete)
        for perm in course_permissions:
            if perm.codename in ['view_course', 'change_course']:
                permissions_to_add.append(perm)
        
        # Права для уроков: view, change (но не add, delete)
        for perm in lesson_permissions:
            if perm.codename in ['view_lesson', 'change_lesson']:
                permissions_to_add.append(perm)

        # Добавляем права в группу
        group.permissions.set(permissions_to_add)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Группе модераторов назначены права: {len(permissions_to_add)} разрешений.'
            )
        )