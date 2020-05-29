"""
Meta social profile urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from post.views import PostViews
from user_profile.views import Files
from .views import ProfileViews


urlpatterns = [
    path('accounts/profile/<str:user_url>/', login_required(ProfileViews.ProfilePage.as_view())),
    path('accounts/profile/<str:user_url>/edit/', login_required(ProfileViews.EditProfile.as_view())),
    path('change_avatar/', login_required(ProfileViews.AvatarManaging.as_view())),
    path('like_marks/', login_required(PostViews.PostUrLikes.as_view())),
    path('accounts/profile/<int:user_id>/send_req/', login_required(ProfileViews.send_friend_request)),

    path('ajax/set_online/', login_required(ProfileViews.set_online)),

    path('files/<str:user_url>/', login_required(Files.all_files))
]
