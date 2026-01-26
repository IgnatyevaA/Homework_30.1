from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwnerOrModerator, IsOwnerAndNotModerator
from .paginators import MaterialsPagination
from .models import Subscription


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с курсами (CRUD)"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination
    
    def get_permissions(self):
        """Разграничение прав доступа по action"""
        if self.action == 'create':
            # Создание только авторизованным пользователям (не модераторам)
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Редактирование владельцу или модератору
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            # Удаление только владельцу (не модератору)
            permission_classes = [IsAuthenticated, IsOwnerAndNotModerator]
        elif self.action in ['list', 'retrieve']:
            # Просмотр всем авторизованным
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Привязка создаваемого курса к текущему пользователю"""
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        """Фильтрация: модераторы видят все, остальные - только свои"""
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            is_moderator = self.request.user.groups.filter(name='moderators').exists()
            if not is_moderator:
                queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonListAPIView(generics.ListAPIView):
    """Получение списка уроков"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MaterialsPagination
    
    def get_queryset(self):
        """Фильтрация: модераторы видят все, остальные - только свои"""
        queryset = Lesson.objects.all()
        if self.request.user.is_authenticated:
            is_moderator = self.request.user.groups.filter(name='moderators').exists()
            if not is_moderator:
                queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение одного урока"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
    def get_queryset(self):
        """Фильтрация: модераторы видят все, остальные - только свои"""
        queryset = Lesson.objects.all()
        if self.request.user.is_authenticated:
            is_moderator = self.request.user.groups.filter(name='moderators').exists()
            if not is_moderator:
                queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]
    
    def perform_create(self, serializer):
        """Привязка создаваемого урока к текущему пользователю"""
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление урока"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
    def get_queryset(self):
        """Фильтрация: модераторы видят все, остальные - только свои"""
        queryset = Lesson.objects.all()
        if self.request.user.is_authenticated:
            is_moderator = self.request.user.groups.filter(name='moderators').exists()
            if not is_moderator:
                queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerAndNotModerator]
    
    def get_queryset(self):
        """Фильтрация: только свои уроки (модераторы не могут удалять)"""
        queryset = Lesson.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class SubscriptionAPIView(APIView):
    """
    Установка/удаление подписки пользователя на курс (toggle).
    Ожидает: {"course_id": <int>}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        course_item = get_object_or_404(Course, pk=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course_item)

        if subs_qs.exists():
            subs_qs.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)