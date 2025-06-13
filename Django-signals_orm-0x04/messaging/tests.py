from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from .models import Message, Notification

class MessageSignalTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='alice', password='testpass')
        self.receiver = User.objects.create_user(username='bob', password='testpass')

    def test_notification_created_on_message(self):
        message = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hello Bob!')
        notification = Notification.objects.filter(user=self.receiver, message=message)
        self.assertEqual(notification.count(), 1)
        self.assertFalse(notification.first().read)
