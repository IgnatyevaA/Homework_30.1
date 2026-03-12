from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группу модераторов с необходимыми правами'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа модераторов создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа модераторов уже существует.'))

        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        course_permissions = Permission.objects.filter(
            content_type=course_content_type,
        )
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type,
        )

        permissions_to_add = []
        for perm in course_permissions:
            if perm.codename in ['view_course', 'change_course']:
                permissions_to_add.append(perm)

        for perm in lesson_permissions:
            if perm.codename in ['view_lesson', 'change_lesson']:
                permissions_to_add.append(perm)

        group.permissions.set(permissions_to_add)

        self.stdout.write(
            self.style.SUCCESS(
                f'Группе модераторов назначены права: {len(permissions_to_add)} разрешений.'
            )
        )
