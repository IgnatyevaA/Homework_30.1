from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Права доступа: владелец может редактировать, остальные только читать"""
    
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем авторизованным пользователям
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Редактирование только владельцу
        return obj == request.user