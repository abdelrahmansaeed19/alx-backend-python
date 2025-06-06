from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')


conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')


urlpatterns = [
    path('', include(router.urls)),
]
