# messaging/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip new messages

    try:
        old_message = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old_message.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=old_message.content
        )
        instance.edited = True  # Mark message as edited

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Sent and received messages are deleted via CASCADE
    # But message history may still reference edited_by or editor
    MessageHistory.objects.filter(editor=instance).delete()