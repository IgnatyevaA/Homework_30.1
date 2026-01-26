from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_only


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""
    video_url = serializers.URLField(required=False, allow_null=True, validators=[validate_youtube_only])

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_lesson_count(self, instance):
        """Возвращает количество уроков в курсе"""
        return instance.lessons.count()

    def get_is_subscribed(self, instance) -> bool:
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=instance).exists()