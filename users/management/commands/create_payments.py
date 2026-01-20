from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import User, Payment
from materials.models import Course, Lesson
import random


class Command(BaseCommand):
    help = 'Создает тестовые данные для платежей'

    def handle(self, *args, **options):
        # Получаем или создаем пользователей
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('Нет пользователей в базе. Создайте пользователей сначала.'))
            return

        # Получаем курсы и уроки
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not courses and not lessons:
            self.stdout.write(self.style.WARNING('Нет курсов и уроков в базе. Создайте курсы и уроки сначала.'))
            return

        # Создаем платежи
        payment_methods = ['cash', 'transfer']
        payments_created = 0

        for i in range(20):  # Создаем 20 платежей
            user = random.choice(users)
            payment_date = timezone.now() - timedelta(days=random.randint(0, 30))
            amount = random.uniform(100.00, 5000.00)
            payment_method = random.choice(payment_methods)

            # Выбираем либо курс, либо урок
            paid_course = None
            paid_lesson = None

            if courses and random.choice([True, False]):
                paid_course = random.choice(courses)
            elif lessons:
                paid_lesson = random.choice(lessons)

            if paid_course or paid_lesson:
                Payment.objects.create(
                    user=user,
                    payment_date=payment_date,
                    paid_course=paid_course,
                    paid_lesson=paid_lesson,
                    amount=round(amount, 2),
                    payment_method=payment_method
                )
                payments_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {payments_created} платежей.')
        )