"""
Chat views module
"""

import json

from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.http import Http404
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from django.forms import modelformset_factory

from core.forms import CropAvatarForm
from core.views import MetaSocialView

from .tasks import make_admin_task, rm_admin_task, add_to_chat_task, rm_from_chat_task
from .forms import UpdateChatAvatarForm, MessageImageForm, MessageMusicForm
from .models import User, Chat, MessageImages, Image, BytesIO, Music


class Conversations:
    """
    Class containing chat functionality
    """

    class ChatList(MetaSocialView):
        """
        Chat list view
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'chat/chat.html'
            self.context = self.get_menu_context('messages', 'Чаты')

        def get(self, request):
            """
            Processing get request
            """
            self.context['pagename'] = 'Чаты'

            c_user = request.user
            self.context['c_user'] = c_user

            chats = c_user.profile.chats.all().order_by('-messages__date')
            self.context['chats'] = list(dict.fromkeys(chats))
            return render(request, self.template_name, self.context)

    @staticmethod
    def create_chat(request):
        """
        Method for creating chat. Returns rendered responce of chatlist
        """
        if request.method == 'POST':
            if request.POST.get('text'):
                context = {}
                new_chat = Chat.objects.create()
                new_chat.participants.add(request.user)
                new_chat.chat_name = request.POST.get('text')
                new_chat.owner = request.user
                new_chat.save()
                c_user = User.objects.get(id=request.user.id)
                c_user.profile.chats.add(new_chat)
                c_user.save()
                context['c_user'] = c_user
                chats = c_user.profile.chats.all().order_by('-messages__date')
                context['chats'] = list(dict.fromkeys(chats))
            return render(request, 'chat/chatlist.html', context)
        raise Http404()

    @staticmethod
    def remove_chat(request, room_id):
        """
        Method for deleting chat. Redirects to chatlist
        """
        c_room = Chat.objects.get(id=room_id)
        if request.method == 'POST' and request.user == c_room.owner:
            c_room.delete()
            return redirect('/chats/')
        raise Http404()

    @staticmethod
    def make_admin(request, room_id, participant_id):
        """
        Method for giving admin permissions in chat
        """
        if request.method == 'POST':
            make_admin_task.delay(room_id, participant_id)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    @staticmethod
    def rm_admin(request, room_id, participant_id):
        """
        Method for removing admin permissions in chat
        """
        if request.method == 'POST':
            rm_admin_task.delay(room_id, participant_id)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    @staticmethod
    def quit_room(request, room_id):
        """
        Method for quiting room
        """
        if request.method == 'POST':
            c_room = Chat.objects.get(id=room_id)
            c_room.participants.remove(request.user)
            if request.user in c_room.administrators.all():
                c_room.administrators.remove(request.user)
            c_room.save()
            request.user.profile.chats.remove(c_room)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    @staticmethod
    def edit_chat_name(request, room_id):
        """
        Method for editing chat name
        """
        if request.method == 'POST':
            c_room = Chat.objects.get(id=room_id)
            c_room.chat_name = request.POST.get('text')
            c_room.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    @staticmethod
    def chat_move(request, user_id, friend_id):
        """
        Method for redirecting to chat, if chat does not exists creates and redirects to it
        """
        c_user = User.objects.get(id=user_id)
        c_friend = User.objects.get(id=friend_id)
        if request.method == "POST":
            for c_user_chat in c_user.profile.chats.all():
                if c_user_chat in c_friend.profile.chats.all() and c_user_chat.is_dialog:
                    ex_chat = Chat.objects.get(id=c_user_chat.id)
                    return redirect('/chat/go_to_chat/' + str(ex_chat.id) + '/')

            new_chat = Chat.objects.create()

            new_chat.participants.add(c_user)
            new_chat.participants.add(c_friend)
            new_chat.chat_name = c_user.username + ' ' + c_friend.username

            new_chat.is_dialog = True

            new_chat.save()

            c_user.profile.chats.add(new_chat)
            c_friend.profile.chats.add(new_chat)
            return redirect('/chat/go_to_chat/' + str(new_chat.id) + '/')

    @staticmethod
    def add_to_chat(request, room_id, friend_id):
        """
        Method for adding user to chat
        """
        if request.method == 'POST':
            add_to_chat_task.delay(room_id, friend_id)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    @staticmethod
    def remove_from_chat(request, room_id, participant_id):
        """
        Method for removing user from chat
        """
        if request.method == 'POST':
            rm_from_chat_task.delay(room_id, participant_id)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        raise Http404()

    class Room(MetaSocialView):
        """
        Chat view class
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name_dialog = 'chat/message.html'
            self.template_name_conv = 'chat/conv_message.html'

        def get(self, request, room_id):
            """
            Processing get request
            """
            context = self.get_menu_context('messages', 'Чат')
            context['room_name'] = mark_safe(json.dumps(room_id))
            c_room = get_object_or_404(Chat, id=room_id)

            MessageImageFormSet = modelformset_factory(
                MessageImages, form=MessageImageForm, extra=10, max_num=10
            )
            context['formset'] = MessageImageFormSet(queryset=MessageImages.objects.none())
            context['musicform'] = MessageMusicForm()

            if request.user not in c_room.participants.all():
                return HttpResponse('Access denied')

            for participant in c_room.participants.all():
                if participant != request.user:
                    context['first_user'] = participant

            self.pagination_elemetns(
                request,
                c_room.messages.all(),
                context,
                'messages_list',
                20
            )

            context['c_room'] = c_room
            other_chats = list(dict.fromkeys(request.user.profile.chats.all().order_by('-messages__date')))
            other_chats.remove(c_room)
            context['other_chats'] = other_chats[:3]
            context['len_other_chats'] = len(other_chats[:3])

            if c_room.is_dialog:
                return render(request, self.template_name_dialog, context)
            else:
                return render(request, self.template_name_conv, context)

    @staticmethod
    def get_messages(request, room_id):
        """
        Method for getting messages list. Returns rendered responce
        """
        if request.method == 'POST':
            messages = Chat.objects.get(id=room_id).messages.all()

            unread_messages = messages.filter(is_readed=False).exclude(author=request.user)

            for message in unread_messages:
                message.is_readed = True
                message.save()

            return render(request, 'chat/messages_list.html', {'messages_list': messages})
        raise Http404()

    class AvatarManaging(MetaSocialView):
        """
        Managing avatar of chat view
        """

        def __init__(self, **kwargs):
            self.template_name = 'chat/change_avatar.html'
            super().__init__(**kwargs)

        def post(self, request, **kwargs):
            """
            Crop and save avatar of chat
            """
            c_room = Chat.objects.get(id=kwargs['room_id'])
            avatar_form = UpdateChatAvatarForm(request.POST, request.FILES, instance=c_room)
            crop_form = CropAvatarForm(request.POST)
            if crop_form.is_valid() and avatar_form.is_valid():
                avatar_form.save()

                x = float(request.POST.get('x'))
                y = float(request.POST.get('y'))
                w = float(request.POST.get('width'))
                h = float(request.POST.get('height'))

                if request.FILES.get('base_image'):
                    image = Image.open(request.FILES.get('base_image'))
                else:
                    image = Image.open(request.user.profile.base_image)
                cropped_image = image.crop((x, y, w + x, h + y))
                resized_image = cropped_image.resize((256, 256), Image.ANTIALIAS)

                io = BytesIO()

                resized_image.save(io, 'JPEG', quality=60)

                c_room.image.save('image_{}.jpg'.format(c_room.id), ContentFile(io.getvalue()),
                                  save=False)
                c_room.save()

                return redirect('/chat/go_to_chat/' + str(c_room.id))

        def get(self, request, room_id):
            """
            Processing get request
            """
            context = self.get_menu_context('messages', 'Смена аватарки')
            chat_item = get_object_or_404(Chat, id=room_id)

            avatar_form = UpdateChatAvatarForm(instance=chat_item)
            crop_form = CropAvatarForm()

            context['avatar_form'] = avatar_form
            context['crop_form'] = crop_form
            context['chat'] = chat_item

            return render(request, self.template_name, context)

    @staticmethod
    def send_files(request, room_id):
        """
        Method for sending files to chat
        """
        chat_item = get_object_or_404(Chat, id=room_id)
        MessageImageFormset = modelformset_factory(
            MessageImages, form=MessageImageForm, extra=10, max_num=10
        )

        if request.method == "POST":
            message_item = chat_item.messages.create(
                author=request.user,
                message=''
            )
            formset = MessageImageFormset(
                request.POST, request.FILES, queryset=MessageImages.objects.none()
            )

            if formset.is_valid():
                if request.POST.get('music'):
                    for music_id in [int(i) for i in request.POST.get('music').split()]:
                        music_item = get_object_or_404(Music, id=music_id)
                        message_item.music.add(music_item)

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        message_item.images.create(image=image)

                return HttpResponse(message_item.id)
        raise Http404()
