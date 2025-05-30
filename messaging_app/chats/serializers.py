from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number']


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.SerializerMethodField()
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'sender_email', 'message_body', 'sent_at']

    def get_sender_email(self, obj):
        return obj.sender.email if obj.sender else None


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data

    def validate(self, data):
        if not data.get('participants') and self.instance is None:
            raise serializers.ValidationError("A conversation must include at least one participant.")
        return data
