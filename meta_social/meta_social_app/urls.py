from django.urls import path
from .views import *


urlpatterns = [
    path('', index),
    path('get_token/', get_token_page),
]