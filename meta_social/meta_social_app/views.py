"""
View module
"""
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views import View
from simple_search import search_filter
from django.utils import timezone
from .models import Profile, Comment, Message, Community, Like, Chat
from PIL import Image
from django.forms import modelformset_factory

from .models import Post, FriendshipRequest, PostImages, Music
from .forms import ProfileUpdateForm, UserUpdateForm, PostForm, PostImageForm, UploadMusicForm, CropAvatarForm, \
    UpdateAvatarForm, CommunityCreateForm, EditPostImageForm
from io import BytesIO
from django.core.files.base import ContentFile


def get_menu_context(page: str, pagename: str) -> dict:
    """
    Getting context
    :param page: str
    :param pagename: str
    :return: context
    """
    available_pages = [
        'profile',
        'newsfeed',
        'friends',
        'community',
        'music',
        'messages',
        'post',
    ]

    if page not in available_pages:
        raise KeyError

    context = {
        'page': page,
        'messages_count': 0,  # TODO: Вносить количество не прочитанных сообщений
        'pagename': pagename,
    }

    return context


def get_last_act(request, user_item) -> None:
    """
    Get last user's action time
    :param request: request
    :param user_item: User
    :return: None
    """
    if request.method == 'GET' and request.user == user_item:
        user_item.profile.last_act = timezone.now()
        user_item.profile.save()


class Index(View):
    """
    Index Class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'index.html'

    def get(self, request) -> render:
        """
        Index page view
        :param request: request
        :return: render
        """
        context = get_menu_context('newsfeed', 'Главная')
        context['pagename'] = "Главная"

        PostImageFormSet = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10)

        context['postform'] = PostForm()
        context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())
        context['action_type'] = '/post/create/'

        return render(request, self.template_name, context)


@login_required
def logout_track(request, user_id) -> redirect:
    """
    When user logs out, time is written to a database
    :param request: request
    :param user_id: id
    :return: redirect
    """
    user_item = User.objects.get(id=user_id)
    user_item.profile.last_logout = timezone.now()
    user_item.profile.save()
    return redirect('/accounts/logout/')


class ProfileViews:
    """
    ProfileViews
    """

    class ProfilePage(View):
        def __init__(self, **kwargs):
            self.template_name = 'profile/profile_page.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs) -> render:
            """
            User profile view.
            :param request: request
            :param user_id: id
            :return: context
            """
            if not User.objects.filter(id=kwargs['user_id']).exists():
                raise Http404()

            context = get_menu_context('profile', 'Профиль')
            context['profile'] = Profile.objects.get(user=kwargs['user_id'])
            user_item = User.objects.get(id=kwargs['user_id'])
            context['c_user'] = user_item
            context['is_online'] = context['profile'].check_online_with_afk()
            print(context['is_online'])
            get_last_act(request, user_item)

            PostImageFormSet = modelformset_factory(
                PostImages, form=PostImageForm, extra=10, max_num=10)

            pass_add_to_friends = False

            is_in_blacklist = False

            if user_item != request.user:
                if request.user not in user_item.profile.friends.all():
                    pass_add_to_friends = True
                if request.user in user_item.profile.blacklist.all():
                    is_in_blacklist = True

            context['is_in_blacklist'] = is_in_blacklist
            context['is_friend'] = True if request.user in user_item.profile.friends.all() \
                                           and request.user != user_item else False
            context['pass_add_to_friends'] = pass_add_to_friends

            context['postform'] = PostForm()
            context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

            context['action_type'] = '/post/create/'

            return render(request, self.template_name, context)

    class EditProfile(View):
        """
        EditProfile class
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'profile/edit_profile.html'
            self.profile = None
            self.previous_birth = None

        def post(self, request, **kwargs) -> redirect:
            """
            Processing post request
            :param request: request
            :param kwargs: attrs
            :return:
            """

            self.previous_birth = User.objects.get(
                id=kwargs['user_id']).profile.birth
            user_form = UserUpdateForm(
                request.POST, instance=User.objects.get(id=kwargs['user_id']))
            self.profile = Profile.objects.get(user=kwargs['user_id'])

            self.profile.show_email = False if request.POST.get(
                'show_email') is None else True

            profile_form = ProfileUpdateForm(request.POST,
                                             instance=self.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()

                if self.profile.birth is None:
                    self.profile.birth = self.previous_birth
                    self.profile.save()

                return redirect('/accounts/profile/' + str(kwargs['user_id']))

        def get(self, request, **kwargs) -> render:
            """
            Processing get request
            :param request: request
            :param kwargs: attrs
            :return: render
            """
            context = get_menu_context('profile', 'Редактирование профиля')
            context['profile'] = Profile.objects.get(user=kwargs['user_id'])
            context['uedit'] = User.objects.get(id=kwargs['user_id'])
            context['user_form'] = UserUpdateForm(
                instance=User.objects.get(id=kwargs['user_id'])
            )
            context['profile_form'] = ProfileUpdateForm(
                instance=Profile.objects.get(user=kwargs['user_id']))
            self.previous_birth = User.objects.get(
                id=kwargs['user_id']).profile.birth
            get_last_act(request, context['uedit'])

            return render(request, self.template_name, context)

    class AvatarManaging(View):
        def __init__(self, **kwargs):
            self.context = get_menu_context('profile', 'Смена аватарки')
            self.template_name = 'profile/change_avatar.html'
            super().__init__(**kwargs)

        def post(self, request):
            avatar_form = UpdateAvatarForm(request.POST, request.FILES, instance=request.user.profile)
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

                try:
                    resized_image.save(io, 'JPEG', quality=100)
                    request.user.profile.image.save('image_{}.jpg'.format(request.user.id), ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()
                except:
                    resized_image.save(io, 'PNG', quality=100)
                    request.user.profile.image.save('image_{}.png'.format(request.user.id), ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()

                return redirect('/accounts/profile/' + str(request.user.id))

        def get(self, request):
            avatar_form = UpdateAvatarForm()
            crop_form = CropAvatarForm()

            self.context['avatar_form'] = avatar_form
            self.context['crop_form'] = crop_form

            return render(request, self.template_name, self.context)


class PostViews:
    """
    PostViews
    """

    class PostView(View):
        """
        PostView
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/full_post.html'

        def get(self, request, **kwargs) -> render:
            context = get_menu_context('post', 'Пост')
            context['post'] = Post.objects.get(id=kwargs['post_id'])

            return render(request, self.template_name, context)

    class PostEdit(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'post/post_edit.html'
            self.context = get_menu_context('post', 'Редактирование поста')

        def post(self, request, **kwargs):
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            PostImageFormSet = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )

            postform = PostForm(request.POST)
            formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImages.objects.none())

            if request.method == 'POST':
                if postform.is_valid() and formset.is_valid():
                    postform.save()
                    
                    for form in formset.ordered_forms:
                        print(form.cleaned_data)
                        if form.cleaned_data['image'] is None:
                            form.cleaned_data['id'].order = form.cleaned_data['ORDER']
                            form.cleaned_data['id'].save()
                        elif form.cleaned_data['image'] == False:
                            if form.cleaned_data['id']:
                                form.cleaned_data['id'].delete()
                        else:
                            if form.cleaned_data['id']:
                                form.cleaned_data['id'].image = form.cleaned_data['image']
                                form.cleaned_data['id'].save()
                            else:
                                item = PostImages(
                                    post=post_item,
                                    order=form.cleaned_data['ORDER'],
                                    image=form.cleaned_data['image']
                                )
                                item.save()
                    
            self.context['postform'] = PostForm(instance=post_item)
            initial_images = [{'image': i.image} for i in post_item.get_images() if i.image]
            self.context['formset'] = PostImageFormSet(initial=initial_images)

            return render(request, self.template_name, self.context)

        def get(self, request, **kwargs):
            post_item = get_object_or_404(Post, id=kwargs['post_id'])
            PostImageFormSet = modelformset_factory(
                PostImages, form=EditPostImageForm, extra=0, max_num=10, can_order=True
            )
            
            self.context['postform'] = PostForm(instance=post_item)
            initial_images = [{'image': i.image} for i in post_item.get_images() if i.image]
            self.context['formset'] = PostImageFormSet(initial=initial_images)
            
            return render(request, self.template_name, self.context)


    class PostAjax(View):
        @staticmethod
        def post(request, **kwargs):
            if request.method == "POST":
                if len(request.POST.get('text')) > 0:
                    comment_item = Comment(
                        text=request.POST.get('text'),
                        post=Post.objects.get(id=kwargs['post_id']),
                        user=request.user
                    )
                    comment_item.save()

                    json_response = json.dumps({'id': comment_item.user.id,
                                                'username': comment_item.user.username,
                                                'text': comment_item.text,
                                                'date': str(comment_item.date)})

                    return HttpResponse(json_response, content_type="application/json")
                raise Http404()

    @staticmethod
    def post_new(request):
        """
        Function for creating post
        :param request: request
        :return: HttpResponseRedirect
        """
        PostImageFormSet = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10)

        if request.method == "POST":
            postForm = PostForm(request.POST)
            formset = PostImageFormSet(
                request.POST, request.FILES, queryset=PostImages.objects.none()
            )

            if postForm.is_valid() and formset.is_valid():
                post_form = postForm.save(commit=False)
                post_form.user = request.user
                post_form.save()

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImages(post=post_form, image=image)
                        photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def post_remove(request, post_id) -> HttpResponseRedirect:
        """
        Removing a post using Ajax
        :param request: request
        :param post_id: id of a post want to be deleted
        :return: HttpResponseRedirect
        """
        if request.method == "POST":
            Post.objects.get(id=post_id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    @staticmethod
    def like_post(request, post_id):
        if request.method == 'POST':
            post_item = get_object_or_404(Post, id=post_id)

            if post_item in request.user.profile.liked_posts.all():
                request.user.profile.liked_posts.remove(post_item)
                post_item.likes.all().get(user=request.user).delete()

                return HttpResponse('unliked')
            else:
                post_item.likes.create(user=request.user)
                request.user.profile.liked_posts.add(post_item)

                return HttpResponse('liked')

        raise Http404()


class MusicViews:
    class MusicList(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_list.html'

        def get(self, request, **kwargs):
            context = get_menu_context('music', 'Музыка')

            context['c_user'] = User.objects.get(id=kwargs['user_id'])
            context['music_list'] = User.objects.get(id=kwargs['user_id']).profile.get_music_list()

            return render(request, self.template_name, context)

    class MusicUpload(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_upload.html'

        @login_required
        def post(self, request):
            form = UploadMusicForm(request.POST, request.FILES)
            if form.is_valid():
                music = form.save(commit=False)
                music.user = request.user
                music.save()

        def get(self, request):
            context = get_menu_context('music', 'Загрузка музыки')

            context['form'] = UploadMusicForm()

            return render(request, self.template_name, context)


class Conversations:
    class ChatList(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'chat/chat.html'

        def get(self, request, **kwargs):
            context = {}

            c_user = User.objects.get(id=kwargs['user_id'])
            context['c_user'] = c_user

            return render(request, self.template_name, context)

    @staticmethod
    def chat_move(request, user_id, friend_id):
        c_user = User.objects.get(id=user_id)
        c_friend = User.objects.get(id=friend_id)
        if request.method == "POST":
            for c_user_chat in c_user.profile.chats.all():
                if c_user_chat in c_friend.profile.chats.all():
                    ex_chat = Chat.objects.get(id=c_user_chat.id)
                    return redirect('/chat/go_to_chat/' + str(ex_chat.id) + '/')

            new_chat = Chat.objects.create(
                first_user=c_user,
                second_user=c_friend
            )

            new_chat.save()
            c_user.profile.chats.add(new_chat)
            c_friend.profile.chats.add(new_chat)
            return redirect('/chat/go_to_chat/' + str(new_chat.id) + '/')

    class Room(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'chat/message.html'

        def get(self, request, room_id):
            context = {'room_name': mark_safe(json.dumps(room_id))}
            c_room = Chat.objects.get(id=room_id)
            context['first_user'] = c_room.first_user if c_room.first_user != request.user else c_room.second_user
            context['messages_list'] = c_room.messages.all()
            return render(request, self.template_name, context)

    @staticmethod
    def get_messages(request, room_id):
        if request.method == 'POST':
            messages = Chat.objects.get(id=room_id).messages.all()

            return render(request, 'chat/messages_list.html', {'messages_list': messages})
        raise Http404()


class Communities:
    class CommunityView(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'community/community_page.html'

        def get(self, request, community_id):
            context = get_menu_context('community', 'Сообщество')

            context['community'] = get_object_or_404(Community, id=community_id)

            PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10, max_num=10)

            context['postform'] = PostForm()
            context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

            context['action_type'] = '/post/create/{}/'.format(community_id)

            return render(request, self.template_name, context)

    class CommunityCreate(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'community/community_create.html'

        @staticmethod
        def post(request):
            form = CommunityCreateForm(request.POST)
            if form.is_valid():
                community = Community(
                    name=request.POST.get('name'),
                    info=request.POST.get('info'),
                    country=request.POST.get('country'),
                    owner=request.user
                )
                community.save()
                community.users.add(request.user)
                request.user.profile.communities.add(community)
                return redirect('/community/{}/'.format(community.id))

        def get(self, request):
            context = get_menu_context('community', 'Создание сообщества')
            context['form'] = CommunityCreateForm()
            return render(request, self.template_name, context)

    class CommunityList(View):
        def __init__(self, **kwargs):
            self.context = {}
            self.template_name_get = 'community/community_list.html'
            self.template_name_post = 'community/search.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs):
            self.context = get_menu_context('community', 'Список сообществ')
            self.context['c_user'] = get_object_or_404(User, id=kwargs['user_id'])
            return render(request, 'community/community_list.html', self.context)

        def post(self, request, **kwargs):
            self.context['matching'] = True
            if not request.POST.get('query'):
                self.context['matching'] = False
                return render(request, 'community/search.html', self.context)
            query = request.POST.get('query')
            search_fields = ['name']
            self.context['c_matches'] = Community.objects.filter(search_filter(search_fields, query))

            return render(request, 'community/search.html', self.context)

    @staticmethod
    def community_join(request, community_id):
        community = get_object_or_404(Community, id=community_id)
        if request.user not in community.users.all():
            community.users.add(request.user)
            request.user.profile.communities.add(community)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def community_leave(request, community_id):
        community = get_object_or_404(Community, id=community_id)
        if request.user in community.users.all():
            community.users.remove(request.user)
            request.user.profile.communities.remove(community)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def post_community_new(request, community_id):
        """
        Function for creating post
        :param request: request
        :return: HttpResponseRedirect
        """

        community = get_object_or_404(Community, id=community_id)

        PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10, max_num=10)

        if request.method == "POST":
            postForm = PostForm(request.POST)
            formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImages.objects.none())

            if postForm.is_valid() and formset.is_valid():
                post_form = postForm.save(commit=False)
                post_form.community = community
                post_form.save()

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImages(post=post_form, image=image)
                        photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class GlobalSearch(View):
    def __init__(self, **kwargs):
        self.template_name = 'search_list.html'
        super().__init__(**kwargs)

    def post(self, request):
        if request.POST.get('query'):
            context = {}
            query = request.POST.get('query')

            search_fields = ['username', 'first_name', 'last_name']
            context['users'] = User.objects.filter(search_filter(search_fields, query)).exclude(id=request.user.id)

            search_fields = ['artist', 'title']
            context['music'] = Music.objects.filter(search_filter(search_fields, query))

            search_fields = ['name']
            context['communities'] = Community.objects.filter(search_filter(search_fields, query))

            return render(request, self.template_name, context)

    def get(self, request):
        raise Http404()


class FriendsViews:
    @staticmethod
    def get_render(request, context):
        context['matching'] = True
        if not request.POST.get('query'):
            context['matching'] = False
            return render(request, 'friends/list.html', context)

        query = request.POST.get('query')
        search_fields = ['username', 'first_name', 'last_name']

        context['f_matches'] = User.objects.filter(search_filter(search_fields, query)).exclude(id=request.user.id)

        return render(request, 'friends/list.html', context)

    class FriendsList(View):
        def __init__(self, **kwargs):
            self.template_name = 'friends/friends_list.html'
            self.context = get_menu_context('friends', 'Список друзей')
            super().__init__(**kwargs)

        def get(self, request, **kwargs):
            self.context['c_user'] = User.objects.get(id=kwargs['user_id'])
            return render(request, self.template_name, self.context)

        def post(self, request, **kwargs):
            self.context['c_user'] = User.objects.get(id=kwargs['user_id'])
            return FriendsViews.get_render(request, self.context)

    class FriendsRequests(View):
        def __init__(self, **kwargs):
            self.template_name = 'friends/requests.html'
            super().__init__(**kwargs)

        def get(self, request):
            context = get_menu_context('friends', 'Заявки в друзья')

            context['c_user'] = request.user
            context['friendship'] = {
                'incoming': request.user.profile.friendship_inbox_requests(),
                'outcoming': request.user.profile.friendship_outbox_requests(),
            }

            return render(request, self.template_name, context)

    class FriendsBlacklist(View):
        def __init__(self, **kwargs):
            self.template_name = 'friends/blacklist.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs) -> render:
            """
            Friends_blacklist view
            :param user_id: user in blacklist od
            :param request: request
            :return: render
            """
            context = get_menu_context('friends', 'Черный список')

            c_user = get_object_or_404(User, id=kwargs['user_id'])
            context['c_user'] = c_user

            return render(request, self.template_name, context)

    class SendFriendshipRequest(View):
        def __init__(self, **kwargs):
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs) -> redirect:
            """
            Sending friendship request view
            :param request: request
            :param user_id: id
            :return: redirect
            """

            self.user_item = get_object_or_404(User, id=kwargs['user_id'])

            if not FriendshipRequest.objects.filter(from_user=self.user_item, to_user=request.user).exists():
                if not FriendshipRequest.objects.filter(from_user=request.user, to_user=self.user_item).exists():
                    item = FriendshipRequest(
                        from_user=request.user,
                        to_user=self.user_item,
                    )

                    item.save()

                    return FriendsViews.get_render(request, {'c_user': request.user})

        def get(self, request, **kwargs):
            raise Http404()

    class AcceptRequest(View):
        def __init__(self, **kwargs):
            self.user_item = None
            super().__init__(**kwargs)

        def post(self, request, **kwargs) -> redirect:
            """
            Accept_request view
            :param request: request
            :param request_id: id
            :return: redirect
            """
            if request.method == 'POST':
                user_item = get_object_or_404(User, id=kwargs['user_id'])

                if FriendshipRequest.objects.filter(from_user=user_item, to_user=request.user).exists():
                    request_item = FriendshipRequest.objects.get(
                        from_user=user_item, to_user=request.user)
                elif FriendshipRequest.objects.filter(from_user=request.user, to_user=user_item).exists():
                    request_item = FriendshipRequest.objects.get(
                        from_user=request.user, to_user=user_item)
                else:
                    raise Http404()

                first_user = User.objects.get(id=request_item.from_user.id)
                second_user = User.objects.get(id=request_item.to_user.id)
                first_user.profile.friends.add(second_user)
                second_user.profile.friends.add(first_user)

                request_item.delete()

                return FriendsViews.get_render(request, {'c_user': request.user})

        def get(self, request, **kwargs):
            raise Http404()

    @staticmethod
    def cancel_request(request, user_id):
        if request.method == 'POST':
            user_item = get_object_or_404(User, id=user_id)

            if FriendshipRequest.objects.filter(from_user=user_item, to_user=request.user).exists():
                request_item = FriendshipRequest.objects.get(
                    from_user=user_item, to_user=request.user)
            elif FriendshipRequest.objects.filter(from_user=request.user, to_user=user_item).exists():
                request_item = FriendshipRequest.objects.get(
                    from_user=request.user, to_user=user_item)
            else:
                raise Http404()

            request_item.delete()

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()

    @staticmethod
    def remove_friend(request, user_id) -> redirect:
        """
        Remove_friend view
        :param request: request
        :param user_id: id
        :return: redirect
        """
        if request.method == 'POST':
            user_item = get_object_or_404(User, id=user_id)

            if user_item in request.user.profile.friends.all():
                request.user.profile.friends.remove(user_item)
                user_item.profile.friends.remove(request.user)
            else:
                raise Http404()

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()

    @staticmethod
    def blacklist_add(request, user_id):
        """
        Blacklist_add view
        :param request: request
        :param user_id: id
        """

        if request.method == 'POST':
            user_for_blacklist = get_object_or_404(User, id=user_id)

            if user_for_blacklist in request.user.profile.friends.all():
                FriendsViews.remove_friend(request, user_id)

            request.user.profile.blacklist.add(user_for_blacklist)
            request.user.save()

            return FriendsViews.get_render(request, {'c_user': request.user})
        raise Http404()

    @staticmethod
    def blacklist_remove(request, user_id):
        """
        Blacklist_remove view
        :param request: request
        :param user_id: id
        """
        if request.method == 'POST':
            user_to_remove = get_object_or_404(User, id=user_id)

            request.user.profile.blacklist.remove(user_to_remove)

            return FriendsViews.get_render(request, {'c_user': request.user})

        raise Http404()
