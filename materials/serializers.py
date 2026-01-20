from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_lesson_count(self, instance):
        """Возвращает количество уроков в курсе"""
        return instance.lessons.count()