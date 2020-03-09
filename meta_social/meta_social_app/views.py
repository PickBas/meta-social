from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from simple_search import search_filter
from django.utils import timezone
from .models import Profile
from PIL import Image

from .models import Friend, Post
from .forms import PostForm, ProfileUpdateForm, UserUpdateForm


def get_menu_context(page):
    available_pages = [
        'profile',
        'newsfeed',
        'friends',
    ]

    if page not in available_pages:
        raise KeyError

    context = {
        'page': page,
        'messages_count': 0,  # TODO: Вносить количество не прочитанных сообщений
    }

    return context


@login_required
def index(request):
    context = get_menu_context('newsfeed')

    context['news'] = request.user.profile.get_newsfeed()
    context['pagename'] = "Главная"
    print(context['news'])

    return render(request, 'index.html', context)


@login_required
def profile(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = get_menu_context('profile')
    context['profile'] = Profile.objects.get(user=user_id)
    user_item = User.objects.get(id=user_id)
    context['c_user'] = user_item
    context['pagename'] = "Профиль"

    return render(request, 'profile/profile_page.html', context)


class ImageManage():
    def __init__(self, user_id, profile, image):
        self.fs = FileSystemStorage()
        self.path = 'avatars/users/' + str(user_id) + '.'
        self.profile = profile
        self.image = image

    def remove_old_avatar(self):
        if self.profile.avatar.name != 'avatars/users/0.png':
            self.fs.delete(self.profile.avatar.path)

    def save_avatar(self):
        self.fs.save(self.path, self.image)
        self.profile.avatar = self.path
        self.profile.save()

    def resize_image(self):
        self.image = Image.open(self.profile.avatar)
        size = (200, 200)
        self.image = self.image.resize(size, Image.ANTIALIAS)
        self.image.save(self.profile.avatar.path)

    def process_img(self):
        if self.image.size <= 5000000 and self.image.content_type.split('/')[0] == 'image':
            img_name, img_extension = self.image.name.split('.')
            self.path += img_extension
            self.remove_old_avatar()
            self.save_avatar()
            self.resize_image()


class EditProfile(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'profile/edit_profile.html'
        self.profile = None

    def post(self, request, **kwargs):

        user_form = UserUpdateForm(request.POST, instance=User.objects.get(id=kwargs['user_id']))
        self.profile = Profile.objects.get(user=kwargs['user_id'])

        self.profile.show_email = False if request.POST.get('show_email') is None else True

        try:
            img_manage = ImageManage(kwargs['user_id'], self.profile, request.FILES['avatar'])
            img_manage.process_img()
        except Exception:
            pass

        profile_form = ProfileUpdateForm(request.POST, instance=Profile.objects.get(user=kwargs['user_id']))

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/accounts/profile/' + str(kwargs['user_id']))

    def get(self, request, **kwargs):
        context = {'profile': Profile.objects.get(user=kwargs['user_id']),
                   'uedit': User.objects.get(id=kwargs['user_id']), 'pagename': "Редактировать профиль",
                   'user_form': UserUpdateForm(instance=User.objects.get(id=kwargs['user_id'])),
                   'profile_form': ProfileUpdateForm(instance=Profile.objects.get(user=kwargs['user_id']))}

        return render(request, self.template_name, context)


@login_required
def add_friend(request, operation, pk):
    new_friend = User.objects.get(pk=pk)
    if operation == 'add':
        Friend.make_friend(request.user, new_friend)
    if operation == 'remove':
        Friend.lose_friend(request.user, new_friend)
    return redirect('/')


@login_required
def friends_list(request, user_id):
    context = get_menu_context('friends')
    context['pagename'] = "Список друзей"
    context['c_user'] = User.objects.get(id=user_id)

    return render(request, 'friends/friends_list.html', context)


@login_required
def friends_search(request):
    context = get_menu_context('friends')
    context['pagename'] = "Поиск друзей"
    if request.method == 'POST':
        if request.POST.get('name'):
            query = request.POST.get('name')
            search_fields = ['username', 'first_name', 'last_name']

            matches = User.objects.filter(search_filter(search_fields, query))

            context['matches'] = matches

    return render(request, 'friends/search.html', context)


@login_required
def friends_requests(request):
    context = get_menu_context('friends')
    context['pagename'] = "Заявки в друзья"
    return render(request, 'friends/requests.html', context)


@login_required
def friends_blacklist(request):
    context = get_menu_context('friends')
    context['pagename'] = "Черный список"
    return render(request, 'friends/blacklist.html', context)


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts, 'pagename': "Посты"})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.date = timezone.now()
            post.save()
    else:
        form = PostForm()
    return render(request, 'post_edit.html', {'form': form, "pagename": "Посты"})
