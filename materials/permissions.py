from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Права доступа для модераторов"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Права доступа для владельца объекта"""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """Права доступа для владельца или модератора"""
    
    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()
        is_owner = obj.owner == request.user
        return is_owner or is_moderator


class IsOwnerAndNotModerator(permissions.BasePermission):
    """Права доступа: только владелец и не модератор"""
    
    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()
        is_owner = obj.owner == request.user
        return is_owner and not is_moderator