from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render
import vk
import requests


def get_facebook_feed(user):
    id = user.profile.get_social_data('facebook')['id']
    token = user.profile.get_token('facebook')

    fields = ','.join([
        'id',
        'message',
        'created_time',
        'picture',
    ])

    feed = requests.get(
        'https://graph.facebook.com/{}/feed?access_token={}&fields={}'.format(id, token, fields)
    )

    return feed.json()


@login_required
def index(request):
    context = {}

    if 'facebook' in request.user.profile.get_social_accounts():
        context['posts'] = get_facebook_feed(request.user)['data']

    if 'vk' in request.user.profile.get_social_accounts():
        session = vk.Session(access_token=request.user.profile.get_token('vk'))

        api = vk.API(session)
        print(api.users.get(user_id=1,v="5.103"))
        context['posts'] = api.wall.get(v="5.103")

    return render(request, 'index.html', context)


@login_required
def profile(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        raise Http404()

    context = {}

    user_item = User.objects.get(id=user_id)

    return render(request, 'profile.html', context)
