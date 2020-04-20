"""
View module
"""
import json
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse, JsonResponse

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.views import View
from simple_search import search_filter
from django.utils import timezone
from django.urls import reverse
from .models import Profile, Comment, Messages, Community
from PIL import Image
from django.forms import modelformset_factory

from .models import Friend, Post, FriendshipRequest, PostImages, Music
from .forms import ProfileUpdateForm, UserUpdateForm, PostForm, PostImageForm, UploadMusicForm, CropAvatarForm, UpdateAvatarForm, CommunityCreateForm
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


@login_required
def index(request) -> render:
    """
    Index page view
    :param request: request
    :return: render
    """
    context = get_menu_context('newsfeed', 'Главная')
    context['pagename'] = "Главная"

    PostImageFormSet = modelformset_factory(
        PostImages, form=PostImageForm, extra=10)

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())
    context['action_type'] = '/post/create/'

    return render(request, 'index.html', context)


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


@login_required
def profile(request, user_id) -> render:
    """
    User profile view.
    :param request: request
    :param user_id: id
    :return: context
    """
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = get_menu_context('profile', 'Профиль')
    context['profile'] = Profile.objects.get(user=user_id)
    user_item = User.objects.get(id=user_id)

    context['c_user'] = user_item
    context['is_online'] = context['profile'].check_online_with_afk()
    get_last_act(request, user_item)

    PostImageFormSet = modelformset_factory(
        PostImages, form=PostImageForm, extra=10)

    pass_add_to_friends = False

    is_in_blacklist = False

    if user_item != request.user:
        if request.user not in user_item.profile.friends():
            pass_add_to_friends = True
        if request.user in user_item.profile.blacklist.all():
            is_in_blacklist = True

    context['is_in_blacklist'] = is_in_blacklist
    context['is_friend'] = True if request.user in user_item.profile.friends() and request.user != user_item else False
    context['pass_add_to_friends'] = pass_add_to_friends

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

    context['action_type'] = '/post/create/'

    return render(request, 'profile/profile_page.html', context)


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

        try:
            img_manage = ImageManage(
                kwargs['user_id'], self.profile, request.FILES['avatar'])
            img_manage.process_img()
        except Exception:
            pass

        profile_form = ProfileUpdateForm(request.POST,
                                         instance=self.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            tmp_user = User.objects.get(id=kwargs['user_id'])

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


@login_required
def post_view(request, post_id):
    context = get_menu_context('post', 'Пост')
    context['pagename'] = 'Пост'
    context['post'] = Post.objects.get(id=post_id)

    return render(request, 'full_post.html', context)


@login_required
def post_ajax(request, post_id):
    if request.method == "POST":
        if len(request.POST.get('text')) > 0:
            comment_item = Comment(
                text=request.POST.get('text'),
                post=Post.objects.get(id=post_id),
                user=request.user
            )
            comment_item.save()

            json_response = json.dumps({'id': comment_item.user.id,
                                        'username': comment_item.user.username,
                                        'text': comment_item.text,
                                        'date': str(comment_item.date)})

            return HttpResponse(json_response, content_type="application/json")
        raise Http404()


@login_required
def friends_list(request, user_id) -> render:
    """
    Friend_list view
    :param request: request
    :param user_id: id
    :return: render
    """
    context = get_menu_context('friends', 'Список друзей')
    context['c_user'] = User.objects.get(id=user_id)
    get_last_act(request, context['c_user'])

    return render(request, 'friends/friends_list.html', context)


@login_required
def friends_search(request) -> render:
    """
    Friends_search view
    :param request: request
    :return: render
    """
    context = get_menu_context('friends', 'Поиск друзей')
    if request.method == 'POST':
        if request.POST.get('name'):
            query = request.POST.get('name')
            search_fields = ['username', 'first_name', 'last_name']

            matches = User.objects.filter(search_filter(
                search_fields, query)).exclude(id=request.user.id)
            context['matches'] = matches
            inbox = [
                i.from_user for i in request.user.profile.friendship_inbox_requests()]
            for match in matches:
                context['is_in_requests'] = True if match in inbox else False
                context['is_in_blacklist'] = True if request.user in match.profile.blacklist.all(
                ) else False

    return render(request, 'friends/search.html', context)


@login_required
def friends_requests(request) -> render:
    """
    Friends_requests view
    :param request: request
    :return: render
    """
    print(i.to_user for i in request.user.profile.friendship_inbox_requests())
    context = get_menu_context('friends', 'Заявки в друзья')
    context['pagename'] = 'Заявки в друзья'
    return render(request, 'friends/requests.html', context)


@login_required
def friends_blacklist(request, user_id) -> render:
    """
    Friends_blacklist view
    :param user_id: user in blacklist od
    :param request: request
    :return: render
    """
    context = get_menu_context('friends', 'Черный список')
    c_user = User.objects.get(id=user_id)
    context['c_user'] = c_user
    # for i in c_user.profile.blacklist.all():
    #     print(i.username)
    return render(request, 'friends/blacklist.html', context)


@login_required
def post_new(request):
    """
    Function for creating post
    :param request: request
    :return: HttpResponseRedirect
    """
    PostImageFormSet = modelformset_factory(
        PostImages, form=PostImageForm, extra=10)

    if request.method == "POST":
        postForm = PostForm(request.POST)
        formset = PostImageFormSet(
            request.POST, request.FILES, queryset=PostImages.objects.none())

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


@login_required
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


@login_required
def post_edit(request, post_id) -> HttpResponseRedirect:
    """
    Editing text of a post
    :param request: request
    :param post_id: id of a post want to be edited
    :return: HttpResponseRedirect
    """

    if request.method == 'POST':
        post_to_edit = Post.objects.get(id=post_id)
        post_to_edit.text = request.POST.get('text')
        post_to_edit.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def post_new(request):
    """
    Function for creating post
    :param request: request
    :return: HttpResponseRedirect
    """
    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

    if request.method == "POST":
        postForm = PostForm(request.POST)
        formset = PostImageFormSet(request.POST, request.FILES, queryset=PostImages.objects.none())

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

@login_required
def send_friendship_request(request, user_id) -> redirect:
    """
    Sending friendship request view
    :param request: request
    :param user_id: id
    :return: redirect
    """

    users_item = User.objects.get(id=user_id)

    if request.method == 'POST':
        if not [i.from_user for i in users_item.profile.friendship_inbox_requests()]:
            item = FriendshipRequest(
                from_user=request.user,
                to_user=User.objects.get(id=user_id),
            )

            item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def accept_request(request, user_id) -> redirect:
    """
    Accept_request view
    :param request: request
    :param request_id: id
    :return: redirect
    """
    if request.method == 'POST':
        if not User.objects.filter(id=user_id).exists:
            raise Http404()

        user_item = User.objects.get(id=user_id)

        if FriendshipRequest.objects.filter(from_user=user_item, to_user=request.user).exists():
            request_item = FriendshipRequest.objects.get(
                from_user=user_item, to_user=request.user)
        elif FriendshipRequest.objects.filter(from_user=request.user, to_user=user_item).exists():
            request_item = FriendshipRequest.objects.get(
                from_user=request.user, to_user=user_item)
        else:
            raise Http404()

        friends_item = Friend(
            from_user=request_item.from_user,
            to_user=request_item.to_user,
        )
        friends_item.save()
        request_item.delete()

        return HttpResponse('Success')

    raise Http404()


@login_required
def remove_friend(request, user_id) -> redirect:
    """
    Remove_friend view
    :param request: request
    :param user_id: id
    :return: redirect
    """
    if request.method == 'POST':
        if not User.objects.filter(id=user_id).exists():
            raise Http404()

        user_item = User.objects.get(id=user_id)

        if Friend.objects.filter(from_user=user_item, to_user=request.user).exists():
            Friend.objects.get(from_user=user_item,
                               to_user=request.user).delete()
        elif Friend.objects.filter(from_user=request.user, to_user=user_item).exists():
            Friend.objects.get(from_user=request.user,
                               to_user=user_item).delete()
        else:
            raise Http404()

        return HttpResponse('Success')

    raise Http404()


@login_required
def blacklist_add(request, user_id):
    """
    Blacklist_add view
    :param request: request
    :param user_id: id
    """

    if request.method == 'POST':
        remove_friend(request, user_id)
        main_user = User.objects.get(id=request.user.id)
        user_for_blacklist = User.objects.get(id=user_id)
        main_user.profile.blacklist.add(user_for_blacklist)
        main_user.save()

        return HttpResponse('Success')

    raise Http404()


@login_required
def blacklist_remove(request, user_id):
    """
    Blacklist_remove view
    :param request: request
    :param user_id: id
    """
    if request.method == 'POST':
        user_to_remove = User.objects.get(id=user_id)
        request.user.profile.blacklist.remove(user_to_remove)

        return HttpResponse('Success')

    raise Http404()


@login_required
def change_avatar(request):
    context = get_menu_context('profile', 'Смена аватарки')

    if request.method == 'POST':
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

            resized_image.save(io, 'JPEG', quality=60)

            request.user.profile.image.save('image_{}.jpg'.format(request.user.id), ContentFile(io.getvalue()), save=False)
            request.user.profile.save()
    else:
        avatar_form = UpdateAvatarForm()
        crop_form = CropAvatarForm()

    context['avatar_form'] = avatar_form
    context['crop_form'] = crop_form

    return render(request, 'profile/change_avatar.html', context)


@login_required
def community(request, community_id):
    context = get_menu_context('community', 'Сообщество')

    context['community'] = get_object_or_404(Community, id=community_id)

    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

    context['action_type'] = '/post/create/{}/'.format(community_id)

    return render(request, 'community/community_page.html', context)


@login_required
def music_list(request, user_id):
    context = get_menu_context('music', 'Музыка')

    context['c_user'] = User.objects.get(id=user_id)
    context['music_list'] = User.objects.get(id=user_id).profile.get_music_list()

    return render(request, 'music/music_list.html', context)


@login_required
def music_upload(request):
    context = get_menu_context('music', 'Загрузка музыки')

    if request.method == 'POST':
        form = UploadMusicForm(request.POST, request.FILES)
        if form.is_valid():
            music = form.save(commit=False)

            music.user = request.user
            music.save()

    context['form'] = UploadMusicForm()

    return render(request, 'music/music_upload.html', context)


@login_required
def community_create(request):
    context = get_menu_context('community', 'Создание сообщества')

    if request.method == 'POST':
        form = CommunityCreateForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()
            community.users.add(request.user)
            request.user.profile.communities.add(community)
            return redirect('/community/{}/'.format(community.id))
    context['form'] = CommunityCreateForm()
    return render(request, 'community/community_create.html', context)


@login_required
def community_list(request):
    context = get_menu_context('community', 'Список сообществ')

    return render(request, 'community/community_list.html', context)


@login_required
def community_join(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user not in community.users.all():
        community.users.add(request.user)
        request.user.profile.communities.add(community)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def community_leave(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.user in community.users.all():
        community.users.remove(request.user)
        request.user.profile.communities.remove(community)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def post_community_new(request, community_id):
    """
    Function for creating post
    :param request: request
    :return: HttpResponseRedirect
    """

    community = get_object_or_404(Community, id=community_id)

    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

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


def get_messages_list(from_user, to_user):
    mes1 = Messages.objects.filter(to_user=from_user, from_user=to_user)
    mes2 = Messages.objects.filter(from_user=from_user, to_user=to_user)
    merged_lists = chain(mes1, mes2)
    sorted_lists = sorted(merged_lists, key=lambda item: item.date)

    return sorted_lists


@login_required
def show_chat(request):
    context = get_menu_context('messages', 'Сообщения')

    context['first_user'] = request.user.profile.friends()[0] if request.user.profile.friends() else None
    
    if context['first_user']:
        context['messages_list'] = get_messages_list(context['first_user'], request.user)
    
    return render(request, 'messages/test.html', context)


@login_required
def send_message(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST' and request.POST.get('text'):
        mes = Messages(from_user=request.user, to_user=to_user, message=request.POST.get('text'))
        mes.save()

        messages = get_messages_list(to_user, request.user)

        return render(request, 'messages/messages_list.html', {'messages_list': messages})
    raise Http404()


@login_required
def get_messages(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        messages = get_messages_list(to_user, request.user)

        return render(request, 'messages/messages_list.html', {'messages_list': messages})
    raise Http404()
