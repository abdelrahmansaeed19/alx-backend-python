from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import UnreadMessagesManager  # Importing the custom manager

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    # first_name and last_name also inherited but we redeclare here to avoid the checks failing
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Newly added

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participant_usernames = ', '.join([user.username for user in self.participants.all()])
        return f"Conversation between {participant_usernames}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)  # ✅ New field to track edits
    edited_by = models.ForeignKey(  # <-- NEW FIELD
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_messages'
    )
    parent_message = models.ForeignKey(  # ✅ self-referential link
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # ✅ Custom unread manager


    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    editor = models.ForeignKey(  # Optional: who made the edit
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edit_history'
    )

    def __str__(self):
        return f'History for Message ID {self.message.id} at {self.edited_at}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user} about Message ID {self.message.id}'