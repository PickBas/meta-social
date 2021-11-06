"""
Meta social profile urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from post.views import PostViews
from user_profile.views import Files
from .views import ProfileViews


urlpatterns = [
    path(
        'accounts/profile/<str:user_url>/',
        login_required(ProfileViews.ProfilePage.as_view()),
        name='profile-page'),
    path(
        'accounts/profile/<str:user_url>/edit/',
        login_required(ProfileViews.EditProfile.as_view()),
        name='profile-page-edit'),
    path(
        'change_avatar/',
        login_required(ProfileViews.AvatarManaging.as_view()),
        name='profile-change-avatar'),
    path(
        'like_marks/',
        login_required(PostViews.PostUrLikes.as_view()),
        name='like-set-mark'),
    path(
        'accounts/profile/<int:user_id>/send_req/',
        login_required(ProfileViews.send_friend_request),
        name='friend-request-send'),

    path(
        'ajax/set_online/',
        login_required(ProfileViews.set_online),
        name='ajax-set-online-status'),

    path(
        'files/<str:user_url>/',
        login_required(Files.all_files),
        name='profile-files-page')
]
