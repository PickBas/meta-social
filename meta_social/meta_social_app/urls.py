from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('accounts/profile/<int:user_id>/', profile),
    path(r'connect/<operation>/<pk>/', add_friend),

    path('friends/<int:user_id>/', friends_list),
    path('friends/search/', friends_search),

    # Allauth urls
    path('accounts/', include('allauth.urls')),
]

urlpatterns += staticfiles_urlpatterns()
