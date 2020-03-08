from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
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


def remove_old_avatar(profile, fs):
    if profile.avatar.name != 'avatars/users/0.png':
        fs.delete(profile.avatar.path)
    print(profile.avatar.path)


def save_avatar(profile, fs, path, image):
    fs.save(path, image)
    profile.avatar = path
    profile.save()


def resize_image(image):
    image = Image.open(profile.avatar)
    size = (200, 200)
    image = image.resize(size, Image.ANTIALIAS)
    image.save(profile.avatar.path)


@login_required
def edit_profile(request, user_id):
    context = {'profile': Profile.objects.get(user=user_id), 'uedit': User.objects.get(id=user_id),
               'pagename': "Редактировать профиль"}

    if request.method == 'POST':

        user_form = UserUpdateForm(request.POST, instance=User.objects.get(id=user_id))
        profile = Profile.objects.get(user=user_id)
        profile.show_email = False if request.POST.get('show_email') is None else True

        try:
            image = request.FILES['avatar']
            if image.size <= 5000000 and image.content_type.split('/')[0] == 'image':
                img_name, img_extension = image.name.split('.')
                path = 'avatars/users/' + str(user_id) + img_extension
                fs = FileSystemStorage()

                remove_old_avatar(profile, fs)
                save_avatar(profile, fs, path, image)
                resize_image(image)

        except Exception:
            pass
        profile.save()
        profile_form = ProfileUpdateForm(request.POST, instance=Profile.objects.get(user=user_id))
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/accounts/profile/' + str(user_id))

    else:
        user_form = UserUpdateForm(instance=User.objects.get(id=user_id))
        profile_form = ProfileUpdateForm(instance=Profile.objects.get(user=user_id))
    context['user_form'] = user_form
    context['profile_form'] = profile_form
    return render(request, 'profile/edit_profile.html', context)


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
