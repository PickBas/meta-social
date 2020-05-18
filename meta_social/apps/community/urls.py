"""
Meta social community urls
"""

from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import Communities


urlpatterns = [
    path('community/<str:community_url>/', login_required(Communities.CommunityView.as_view())),
    path('community/user/list/', login_required(Communities.CommunityList.as_view())),
    path('community/user/mylist/', login_required(Communities.my_communities)),
    path('community/user/create/', login_required(Communities.CommunityCreate.as_view())),
    path('community/<str:community_url>/join/', login_required(Communities.community_join)),
    path('community/<str:community_url>/leave/', login_required(Communities.community_leave)),
    path('community/<str:community_url>/change_avatar/', login_required(Communities.AvatarManaging.as_view())),
    path('community/<str:community_url>/edit/', login_required(Communities.EditCommunity.as_view())),
]
