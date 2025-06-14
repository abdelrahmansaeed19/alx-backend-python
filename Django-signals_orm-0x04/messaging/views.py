from django.shortcuts import render

from rest_framework import viewsets, status, filters  # ✅ includes 'status' and 'filters'
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOfMessageOrConversation, IsParticipantOfConversation
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter
from .pagination import MessagePagination
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Prefetch
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page


# Fetch top-level messages and their direct replies in one go
messages = Message.objects.filter(parent_message__isnull=True) \
    .select_related('sender', 'receiver') \
    .prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
    )

@cache_page(60)  # Cache this view for 15 minutes
@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("content")
        receiver_id = request.POST.get("receiver_id")
        parent_id = request.POST.get("parent_id")

        receiver = get_object_or_404(User, id=receiver_id)
        parent_message = None

        if parent_id:
            parent_message = get_object_or_404(Message, id=parent_id)

        Message.objects.create(
            sender=request.user,  # ✅ sets the sender
            receiver=receiver,    # ✅ sets the receiver
            content=content,
            parent_message=parent_message
        )

        return redirect("inbox")  # Replace with your actual redirect
    else:
        users = User.objects.exclude(id=request.user.id)
        return render(request, "messaging/send_message.html", {"users": users})

@login_required
def unread_messages_view(request):

    unread_messages = Message.unread.unread_for_user(request.user).only(
            "id", "sender", "content", "timestamp") # ✅ Using custom manager
    
    return render(request, "messaging/unread_messages.html", {"unread_messages": unread_messages})

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination  # Custom pagination class
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        # Show only conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('pk')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('pk')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('pk')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfMessageOrConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination 
    ordering_fields = ['sent_at']
    
    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if self.request.user not in conversation.participants.all():
            return Message.objects.none()

        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if self.request.user not in conversation.participants.all():
            self.permission_denied(
                self.request,
                message="You are not a participant in this conversation.",
                code=status.HTTP_403_FORBIDDEN
            )

        serializer.save(sender=self.request.user, conversation=conversation)

@login_required
def delete_user(request):
    user = request.user
    logout(request)  # Log user out first
    user.delete()  # Triggers post_delete signal
    return redirect('home')  # Replace with your homepage/view

