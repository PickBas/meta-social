"""
Chat routing
"""

from django.urls import re_path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    re_path(r'wss/chat/(?P<room_name>\w+)/$', ChatConsumer),
]
