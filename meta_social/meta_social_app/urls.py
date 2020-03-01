from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *


urlpatterns = [
    path('', index),
    path('accounts/profile/<int:user_id>/', profile),
    path('accounts/profile/<int:user_id>/second/', profile_second),

    # Allauth urls
    path('accounts/', include('allauth.urls')),
]

urlpatterns += staticfiles_urlpatterns()
