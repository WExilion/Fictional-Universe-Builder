from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrModeratorOrReadOnly(BasePermission):
    moderator_group_name = "Moderators"
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return (
            user.is_authenticated and (
                getattr(obj, "owner", None) == user
                or user.is_superuser
                or user.groups.filter(name=self.moderator_group_name).exists()
            )
        )



