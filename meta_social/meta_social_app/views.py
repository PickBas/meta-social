from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from simple_search import search_filter
from django.utils import timezone

from .models import Friend, Post
from .forms import PostForm


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
        'messages_count': 0, # TODO: Вносить количество не прочитанных сообщений
    }

    return context


@login_required
def index(request):
    context = get_menu_context('newsfeed')

    context['news'] = request.user.profile.get_newsfeed()
    print(context['news'])

    return render(request, 'index.html', context)


@login_required
def profile(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = get_menu_context('profile')

    user_item = User.objects.get(id=user_id)
    context['c_user'] = user_item

    return render(request, 'profile/profile_page.html', context)


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
    context['c_user'] = User.objects.get(id=user_id)

    return render(request, 'friends/friends_list.html', context)


@login_required
def friends_search(request):
    context = get_menu_context('friends')

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

    return render(request, 'friends/requests.html', context)


@login_required
def friends_blacklist(request):
    context = get_menu_context('friends')

    return render(request, 'friends/blacklist.html', context)


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})


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
    return render(request, 'post_edit.html', {'form': form})
