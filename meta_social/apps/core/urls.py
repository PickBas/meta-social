"""
Meta social core urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .views import Index, GlobalSearch


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('ajax/update_nav/', login_required(Index.update_nav)),
    path('ajax/search/', login_required(GlobalSearch.as_view())),
    path('about/',
         TemplateView.as_view(template_name='about_us.html'),
         name='about'),
]
