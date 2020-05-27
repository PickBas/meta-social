"""
Meta social music urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import MusicViews


urlpatterns = [
    path('accounts/profile/<custom_url>/music/', login_required(MusicViews.MusicList.as_view())),
    path('music/upload/', login_required(MusicViews.MusicUpload.as_view())),
    path('music/search/', login_required(MusicViews.MusicSearch.as_view())),
    path('music/<int:music_id>/add/', login_required(MusicViews.add_music)),
    path('music/<int:music_id>/add_from_search/', login_required(MusicViews.add_music_from_search)),
]
