"""
View module
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import Http404

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.views import View
from simple_search import search_filter
from django.utils import timezone
from django.urls import reverse
from .models import Profile
from PIL import Image
from django.forms import modelformset_factory

from .models import Friend, Post, FriendshipRequest, PostImages
from .forms import ProfileUpdateForm, UserUpdateForm, CropImageForm, PostForm, PostImageForm


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

    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

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

    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

    pass_add_to_friends = False

    if user_item != request.user:
        if request.user not in user_item.profile.friends() and request.user not in user_item.profile.blacklist.all():
            pass_add_to_friends = True

    context['pass_add_to_friends'] = pass_add_to_friends

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

    return render(request, 'profile/profile_page.html', context)


class ImageManage:
    """
    Processing images class
    """

    def __init__(self, user_id, profile, image):
        self.file_sys = FileSystemStorage()
        self.path = 'avatars/users/' + str(user_id) + '.'
        self.profile = profile
        self.image = image

    def remove_old_avatar(self) -> None:
        """
        Removing old avatar
        :return: None
        """
        if self.profile.avatar.name != 'avatars/users/0.png':
            self.file_sys.delete(self.profile.avatar.path)

    def save_avatar(self) -> None:
        """
        Saving new avatar
        :return: None
        """
        self.file_sys.save(self.path, self.image)
        self.profile.avatar = self.path
        self.profile.save()

    def resize_image(self) -> None:
        """
        Resizing image to 200x200
        :return: None
        """
        self.image = Image.open(self.profile.avatar)
        size = (200, 200)
        self.image = self.image.resize(size, Image.ANTIALIAS)
        self.image.save(self.profile.avatar.path)

    def process_img(self) -> None:
        """
        Process image
        :return: None
        """
        if self.image.size <= 5000000 and self.image.content_type.split('/')[0] == 'image':
            img_extension = self.image.name.split('.')[1]
            self.path += img_extension
            self.remove_old_avatar()
            self.save_avatar()
            self.resize_image()


class EditProfile(View):
    """
    EditProfile class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'profile/edit_profile.html'
        self.profile = None

    def post(self, request, **kwargs) -> redirect:
        """
        Processing post request
        :param request: request
        :param kwargs: attrs
        :return:
        """

        user_form = UserUpdateForm(request.POST, instance=User.objects.get(id=kwargs['user_id']))
        self.profile = Profile.objects.get(user=kwargs['user_id'])

        self.profile.show_email = False if request.POST.get('show_email') is None else True

        try:
            img_manage = ImageManage(kwargs['user_id'], self.profile, request.FILES['avatar'])
            img_manage.process_img()
        except Exception:
            pass

        profile_form = ProfileUpdateForm(request.POST,
                                         instance=Profile.objects.get(user=kwargs['user_id']))

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
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
        context['profile_form'] = ProfileUpdateForm(instance=Profile.objects.get(user=kwargs['user_id']))
        get_last_act(request, context['uedit'])

        return render(request, self.template_name, context)


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

            matches = User.objects.filter(search_filter(search_fields, query)).exclude(id=request.user.id)
            context['matches'] = matches
            inbox = [i.from_user for i in request.user.profile.friendship_inbox_requests()]
            for match in matches:
                context['is_in_requests'] = True if match in inbox else False

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
                already_sent=True
            )

            item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def accept_request(request, request_id) -> redirect:
    """
    Accept_request view
    :param request: request
    :param request_id: id
    :return: redirect
    """
    if request.method == 'POST':
        try:
            request_item = FriendshipRequest.objects.get(to_user=request_id)
        except Exception:
            try:
                request_item = FriendshipRequest.objects.get(from_user=request_id)
            except Exception:
                request_item = FriendshipRequest.objects.get(id=request_id)
        friends_item = Friend(
            from_user=request_item.from_user,
            to_user=request_item.to_user,
        )
        friends_item.save()
        request_item.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_friend(request, user_id) -> redirect:
    """
    Remove_friend view
    :param request: request
    :param user_id: id
    :return: redirect
    """
    if request.method == 'POST':
        try:
            friend_item = Friend.objects.get(from_user=user_id)
            friend_item.delete()
        except Exception:
            try:
                friend_item = Friend.objects.get(to_user=user_id)
                friend_item.delete()
            except Exception:
                friend_item = Friend.objects.get(id=user_id)
                friend_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def crop_image(request, user_id):
    """
    Function for cropping image
    :param request: request
    :return: HttpResponseRedirect
    """
    if int(request.user.id) != int(user_id):
        raise Http404()

    image = get_object_or_404(Profile, pk=user_id) if user_id else None
    form = CropImageForm(instance=image)

    if request.method == 'POST':
        form = CropImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            image = form.save()
            return HttpResponseRedirect(reverse('crop', args=(image.pk,)))

    context = get_menu_context('profile', 'Смена аватарки')
    context['form'] = form
    context['image'] = image

    return render(request, 'profile/crop.html', context)


def community(request, community_id):
    context = get_menu_context('community', 'Сообщество')

    PostImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=10)

    context['postform'] = PostForm()
    context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

    return render(request, 'community/community_page.html', context)
