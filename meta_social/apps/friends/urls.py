"""
Meta social friends urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import FriendsViews


urlpatterns = [
    path(
        'friends/',
        login_required(FriendsViews.FriendsList.as_view()),
        name='friends-list'),
    path(
        'friends/requests/',
        login_required(FriendsViews.FriendsRequests.as_view()),
        name='friends-requests'),
    path(
        'friends/blacklist/',
        login_required(FriendsViews.FriendsBlacklist.as_view()),
        name='friends-blacklist'),

    path(
        'friends/send_request/<int:user_id>/',
        login_required(FriendsViews.SendFriendshipRequest.as_view()),
        name='friend-send-request'),
    path(
        'friends/accept_request/<int:user_id>/',
        login_required(FriendsViews.AcceptRequest.as_view()),
        name='friend-accept-request'),
    path(
        'friends/cancel_request/<int:user_id>/',
        login_required(FriendsViews.cancel_request),
        name='friend-cancel-request'),
    path(
        'friends/remove_friend/<int:user_id>/',
        login_required(FriendsViews.remove_friend),
        name='friend-remove'),
    path(
        'friends/add_blacklist/<int:user_id>/',
        login_required(FriendsViews.blacklist_add),
        name=''),
    path(
        'friends/remove_blacklist/<int:user_id>/',
        login_required(FriendsViews.blacklist_remove),
        name='friend-remove-from-blacklist'),
]
