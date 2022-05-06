from rest_framework import permissions


class IsAuthorAndStaffOrReadOnly(permissions.BasePermission):
    """
    Доступ для автора, модератора и админа.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        )


class IsAdminOrSuperuser(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'or request.user.is_staff
        return False


class AnyReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
