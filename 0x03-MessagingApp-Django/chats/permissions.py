from rest_framework import permissions

SAFE_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of the conversation
    to perform any actions (GET, POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Get the related conversation
        conversation = getattr(obj, 'conversation', None)

        if conversation:
            if request.method in SAFE_METHODS:
                return request.user in conversation.participants.all()

        # If obj itself is a Conversation
        if hasattr(obj, 'participants'):
            if request.method in SAFE_METHODS:
                return request.user in obj.participants.all()

        return False

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
