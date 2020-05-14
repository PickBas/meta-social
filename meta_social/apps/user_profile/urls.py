from django.urls import path

from .views import *


urlpatterns = [
    path('accounts/profile/<int:user_id>/', login_required(ProfileViews.ProfilePage.as_view())),
    path('accounts/profile/<int:user_id>/edit/', login_required(ProfileViews.EditProfile.as_view())),
    path('accounts/profile/change_avatar/', login_required(ProfileViews.AvatarManaging.as_view())),
    path('accounts/profile/like_marks/', login_required(PostViews.PostUrLikes.as_view())),

    path('ajax/set_online/', login_required(ProfileViews.set_online)),

    path('files/<int:user_id>/', login_required(Files.all_files))
]
