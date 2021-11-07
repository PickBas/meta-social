"""
Celery tasks
"""

from core.celery import app

from .models import Chat, User


@app.task
def make_admin_task(room_id, participant_id):
    """
    Giving admin permissions async
    """
    c_room = Chat.objects.get(id=room_id)
    participant = User.objects.get(id=participant_id)
    c_room.administrators.add(participant)
    c_room.save()


@app.task
def rm_admin_task(room_id, participant_id):
    """
    Removing admin permissions async
    """
    c_room = Chat.objects.get(id=room_id)
    participant = User.objects.get(id=participant_id)
    c_room.administrators.remove(participant)
    c_room.save()


@app.task
def add_to_chat_task(room_id, friend_id):
    """
    Adding to chat async
    """
    c_room = Chat.objects.get(id=room_id)
    c_friend = User.objects.get(id=friend_id)
    c_room.participants.add(c_friend)
    c_room.save()
    c_friend.profile.chats.add(c_room)
    c_friend.save()


@app.task
def rm_from_chat_task(room_id, participant_id):
    """
    Removing from chat async
    """
    c_room = Chat.objects.get(id=room_id)
    c_participant = User.objects.get(id=participant_id)

    c_room.participants.remove(c_participant)
    c_participant.profile.chats.remove(c_room)

    c_room.save()
    c_participant.save()
