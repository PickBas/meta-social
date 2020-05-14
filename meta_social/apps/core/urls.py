"""
Meta social core urls module
"""

from django.urls import path
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('ajax/search/', login_required(GlobalSearch.as_view())),
    path('ajax/update_nav/', login_required(Index.update_nav)),
]
