from django.urls import path, include
#from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, unread_messages_view
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')


conversations_router = routers.NestedSimpleRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')


urlpatterns = [
    path('', include(router.urls)),
    path('inbox/unread/', unread_messages_view, name='unread_messages'),
]
