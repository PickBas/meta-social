"""
Meta social community urls module
"""

from django.urls import path

from .views import *


urlpatterns = [
    path('community/<int:community_id>/', login_required(Communities.CommunityView.as_view())),
    path('community/list/<int:user_id>/', login_required(Communities.CommunityList.as_view())),
    path('community/mylist/', login_required(Communities.my_communities)),
    path('community/create/', login_required(Communities.CommunityCreate.as_view())),
    path('community/<int:community_id>/join/', login_required(Communities.community_join)),
    path('community/<int:community_id>/leave/', login_required(Communities.community_leave)),
    path('community/<int:community_id>/change_avatar/', login_required(Communities.AvatarManaging.as_view())),
    path('community/<int:community_id>/edit/', login_required(Communities.EditCommunity.as_view())),
]
