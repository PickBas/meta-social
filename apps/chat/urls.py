"""
Chat urls module
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import Conversations


urlpatterns = [
    path(
        'chats/',
        login_required(Conversations.ChatList.as_view()),
        name='chat-list'),
    path(
        'chat/create/',
        login_required(Conversations.create_chat),
        name='chat-create'),
    path(
        'chat/<int:room_id>/remove/',
        login_required(Conversations.remove_chat),
        name='chat-remove'),
    path(
        'chat/quit/<int:room_id>/',
        login_required(Conversations.quit_room),
        name='chat-quit'),
    path(
        'chat/<int:room_id>/add/<int:friend_id>/',
        login_required(Conversations.add_to_chat),
        name='chat-add-friend'),
    path(
        'chat/<int:room_id>/remove/<int:participant_id>/',
        login_required(Conversations.remove_from_chat),
        name='chat-remove-member'),
    path(
        'chat/<int:room_id>/makeadmin/<int:participant_id>/',
        login_required(Conversations.make_admin),
        name='chat-make-admin'),
    path(
        'chat/<int:room_id>/rmadmin/<int:participant_id>/',
        login_required(Conversations.rm_admin),
        name='chat-rm-admin'),
    path(
        'chat/change_avatar/<int:room_id>/',
        login_required(Conversations.AvatarManaging.as_view()),
        name='chat-avatar-change'),
    path(
        'chat/edit_chat_name/<int:room_id>/',
        login_required(Conversations.edit_chat_name),
        name='chat-edit-name'),
    path(
        'chats/<int:user_id>/<int:friend_id>/',
        login_required(Conversations.chat_move),
        name='chat-friend-redirect'),
    path(
        'chat/go_to_chat/<int:room_id>/',
        login_required(Conversations.Room.as_view()),
        name='chat-go-to-chat'),
    path(
        'chat/go_to_chat/<int:room_id>/get_messages/',
        login_required(Conversations.get_messages),
        name='chat-go-to-chat-get-message'),
    path(
        'chat/go_to_chat/<int:room_id>/send_files/',
        login_required(Conversations.send_files),
        name='chat-go-to-chat-send-files'),
]
