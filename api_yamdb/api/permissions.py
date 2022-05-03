from rest_framework import permissions


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'user'


class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'moderator'
