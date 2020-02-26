from django.urls import path, include
from .views import *


urlpatterns = [
    path('', index),
    path('accounts/profile/<int:user_id>/', profile),

    # Allauth urls
    path('accounts/', include('allauth.urls')),
]
