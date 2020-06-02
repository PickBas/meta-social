"""
Meta social core urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import Index, GlobalSearch, AboutView


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('ajax/update_nav/', login_required(Index.update_nav)),
    path('ajax/search/', login_required(GlobalSearch.as_view())),
    path('about/',  AboutView.as_view(), name='about'),
    # path('aboutform/',
    #      AboutFormView.as_view(),
    #      name='aboutform'),
]
