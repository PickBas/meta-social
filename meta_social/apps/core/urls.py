"""
Meta social core urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import Index, GlobalSearch


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('ajax/update_nav/', login_required(Index.update_nav)),
    path('ajax/search/', login_required(GlobalSearch.as_view())),
    path('send_email/', login_required(Index.send_email))
]
