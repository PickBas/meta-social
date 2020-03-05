from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from simple_search import search_filter

from .models import Friend, Posts


@login_required
def index(request):
    user = User.objects.exclude(id=request.user.id)
    context = {
        'user': user
    }
    #friends =Friend.objects.get(current_user=request.user, )
    return render(request, 'index.html', context)


@login_required
def profile(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = {}

    user_item = User.objects.get(id=user_id)

    return render(request, 'profile.html', context)


@login_required
def profile_second(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = {}

    user_item = User.objects.get(id=user_id)

    return render(request, 'profile_page.html', context)


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
    context = {}
    context['c_user'] = User.objects.get(id=user_id)

    return render(request, 'friends/friends_list.html', context)


@login_required
def friends_search(request):
    context = {}

    if request.method == 'POST':
        if request.POST.get('name'):
            query = request.POST.get('name')
            search_fields = ['username', 'first_name', 'last_name']

            matches = User.objects.filter(search_filter(search_fields, query))

            context['matches'] = matches

    return render(request, 'friends/search.html', context)
