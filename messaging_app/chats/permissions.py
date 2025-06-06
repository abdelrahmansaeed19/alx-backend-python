from rest_framework import permissions


class IsOwnerOfMessageOrConversation(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own messages or conversations.
    """

    def has_object_permission(self, request, view, obj):
        # For Message objects: check if the request user is the sender or recipient
        if hasattr(obj, 'sender') and hasattr(obj, 'recipient'):
            return obj.sender == request.user or obj.recipient == request.user

        # For Conversation objects: check if the request user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        # Default deny if object doesn't match known types
        return False
