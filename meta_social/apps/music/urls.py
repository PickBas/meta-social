"""
Meta social music urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import MusicViews


urlpatterns = [
    path(
        'accounts/profile/<custom_url>/music/',
        login_required(MusicViews.MusicList.as_view()),
        name='profile-music-page'),
    path(
        'music/upload/',
        login_required(MusicViews.MusicUpload.as_view()),
        name='music-upload'),
    path(
        'music/<int:music_id>/add/',
        login_required(MusicViews.add_music),
        name='profile-music-add'),
    path(
        'music/<int:music_id>/add_from_search/',
        login_required(MusicViews.add_music_from_search),
        name='profile-music-add-from-search'),
    path(
        'music/<int:music_id>/remove/',
        login_required(MusicViews.remove),
        name='music-remove'),
]
