from django.urls import path

from .views import *


urlpatterns = [
    path('music/<int:user_id>/', login_required(MusicViews.MusicList.as_view())),
    path('music/upload/', login_required(MusicViews.MusicUpload.as_view())),
]
