from django.urls import path

from .views import *


urlpatterns = [
    path('friends/<int:user_id>/', login_required(FriendsViews.FriendsList.as_view())),
    path('friends/requests/', login_required(FriendsViews.FriendsRequests.as_view())),
    path('friends/<int:user_id>/blacklist/', login_required(FriendsViews.FriendsBlacklist.as_view())),

    path('friends/send_request/<int:user_id>/', login_required(FriendsViews.SendFriendshipRequest.as_view())),
    path('friends/accept_request/<int:user_id>/', login_required(FriendsViews.AcceptRequest.as_view())),
    path('friends/cancel_request/<int:user_id>/', login_required(FriendsViews.cancel_request)),
    path('friends/remove_friend/<int:user_id>/', login_required(FriendsViews.remove_friend)),
    path('friends/add_blacklist/<int:user_id>/', login_required(FriendsViews.blacklist_add)),
    path('friends/remove_blacklist/<int:user_id>/', login_required(FriendsViews.blacklist_remove)),
]
