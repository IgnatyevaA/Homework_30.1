from django.contrib.auth.models import Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from .models import Course, Lesson, Subscription


class BaseAPITestCase(APITestCase):
    """
    Базовый тестовый класс с созданием пользователей и группы модераторов.
    """

    def setUp(self) -> None:
        super().setUp()
        # Группа модераторов
        self.moderators_group, _ = Group.objects.get_or_create(name="moderators")

        # Обычный пользователь (владелец)
        self.owner = User.objects.create_user(email="owner@example.com", password="pass12345")

        # Другой пользователь
        self.other_user = User.objects.create_user(email="other@example.com", password="pass12345")

        # Модератор
        self.moderator = User.objects.create_user(email="moderator@example.com", password="pass12345")
        self.moderator.groups.add(self.moderators_group)

        # Базовый курс и урок
        self.course = Course.objects.create(title="Test course", description="desc", owner=self.owner)
        self.lesson = Lesson.objects.create(
            title="Test lesson",
            description="lesson desc",
            course=self.course,
            owner=self.owner,
        )


class LessonCRUDTests(BaseAPITestCase):
    """
    Тесты CRUD для уроков с разными правами доступа.
    """

    def test_lesson_list_owner_sees_own_lessons(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем пагинацию и данные
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.lesson.title)

    def test_lesson_list_moderator_sees_all_lessons(self):
        # Добавим ещё один урок другого пользователя
        Lesson.objects.create(
            title="Other lesson",
            description="other",
            course=self.course,
            owner=self.other_user,
        )
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_lesson_create_by_owner_allowed(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson-create")
        payload = {
            "title": "New lesson",
            "description": "new",
            "course": self.course.id,
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.filter(owner=self.owner).count(), 2)

    def test_lesson_create_by_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-create")
        payload = {
            "title": "Mod lesson",
            "description": "mod",
            "course": self.course.id,
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_owner_allowed(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson-retrieve", args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lesson.id)

    def test_lesson_retrieve_moderator_allowed(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-retrieve", args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_owner_allowed(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson-update", args=[self.lesson.id])
        payload = {"title": "Updated title", "course": self.course.id}
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated title")

    def test_lesson_update_moderator_allowed(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-update", args=[self.lesson.id])
        payload = {"title": "Moderator updated", "course": self.course.id}
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Moderator updated")

    def test_lesson_delete_owner_allowed(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("lesson-destroy", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_lesson_delete_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-destroy", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(BaseAPITestCase):
    """
    Тесты функционала подписки на обновления курса.
    """

    def test_subscribe_and_unsubscribe_toggle(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("subscription-toggle")
        payload = {"course_id": self.course.id}

        # Подписка
        response_subscribe = self.client.post(url, payload, format="json")
        self.assertEqual(response_subscribe.status_code, status.HTTP_200_OK)
        self.assertEqual(response_subscribe.data["message"], "подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.owner, course=self.course).exists())

        # Отписка
        response_unsubscribe = self.client.post(url, payload, format="json")
        self.assertEqual(response_unsubscribe.status_code, status.HTTP_200_OK)
        self.assertEqual(response_unsubscribe.data["message"], "подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.owner, course=self.course).exists())

    def test_course_serializer_shows_is_subscribed_flag(self):
        """
        Проверяем, что флаг is_subscribed корректно отображается для текущего пользователя.
        """
        # Сначала подписываем пользователя
        Subscription.objects.create(user=self.owner, course=self.course)
        self.client.force_authenticate(user=self.owner)

        # Получаем детальную информацию о курсе
        url_detail = reverse("course-detail", args=[self.course.id])
        response_detail = self.client.get(url_detail)
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertTrue(response_detail.data.get("is_subscribed"))

        # Для неподписанного пользователя флаг должен быть False
        self.client.force_authenticate(user=self.other_user)
        response_other = self.client.get(url_detail)
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        self.assertFalse(response_other.data.get("is_subscribed"))
