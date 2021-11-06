"""
Meta social post urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from community.views import Communities
from .views import PostViews

urlpatterns = [
    path(
        'post/create/',
        login_required(PostViews.post_new),
        name='profile-post-create'),
    path(
        'post/create/<str:community_url>/',
        login_required(Communities.post_community_new),
        name='community-post-create'),

    path(
        'post/<int:post_id>/',
        login_required(PostViews.PostView.as_view()),
        name='post-page'),
    path(
        'post/<int:post_id>/remove/',
        login_required(PostViews.post_remove),
        name='post-remove'),
    path(
        'post/<int:post_id>/send_comment/',
        login_required(PostViews.send_comment),
        name='post-send-comment'),
    path(
        'post/<int:post_id>/edit/',
        login_required(PostViews.PostEdit.as_view()),
        name='post-edit'),
    path(
        'post/<int:post_id>/rt/',
        login_required(PostViews.rt),
        name='post-repost'),

    path(
        'like/<int:post_id>/',
        login_required(PostViews.like_post),
        name='post-like'),
    path(
        'post/<int:post_id>/get_comments/<int:is_all>/',
        login_required(PostViews.get_comments),
        name='post-comments'),
]
