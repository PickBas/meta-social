"""
Chat urls module
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import Conversations


urlpatterns = [
    path('chats/<str:user_url>/', login_required(Conversations.ChatList.as_view())),
    path('chat/create/', login_required(Conversations.create_chat)),
    path('chat/<int:room_id>/remove/', login_required(Conversations.remove_chat)),
    path('chat/quit/<int:room_id>/', login_required(Conversations.quit_room)),
    path('chat/<int:room_id>/add/<int:friend_id>/', login_required(Conversations.add_to_chat)),
    path('chat/<int:room_id>/remove/<int:participant_id>/', login_required(Conversations.remove_from_chat)),
    path('chat/<int:room_id>/makeadmin/<int:participant_id>/', login_required(Conversations.make_admin)),
    path('chat/<int:room_id>/rmadmin/<int:participant_id>/', login_required(Conversations.rm_admin)),
    path('chat/change_avatar/<int:room_id>/', login_required(Conversations.AvatarManaging.as_view())),
    path('chat/edit_chat_name/<int:room_id>/', login_required(Conversations.edit_chat_name)),
    path('chats/<int:user_id>/<int:friend_id>/', login_required(Conversations.chat_move)),
    path('chat/go_to_chat/<int:room_id>/', login_required(Conversations.Room.as_view())),
    path('chat/go_to_chat/<int:room_id>/get_messages/', login_required(Conversations.get_messages)),
    path('chat/go_to_chat/<int:room_id>/send_files/', login_required(Conversations.send_files)),
]
