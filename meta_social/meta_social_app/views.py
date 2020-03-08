from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, HttpResponse
from django.utils import timezone

from .models import Friend, Post
from .forms import PostForm


@login_required
def index(request):
    context = {}

    context['news'] = request.user.profile.get_newsfeed()

    return render(request, 'index.html', context)


@login_required
def profile(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = {}

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
