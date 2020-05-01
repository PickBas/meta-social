from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.conf import settings
from .views import *


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('accounts/profile/<int:user_id>/', login_required(ProfileViews.ProfilePage.as_view())),
    path('accounts/profile/<int:user_id>/edit/', login_required(ProfileViews.EditProfile.as_view())),
    path('accounts/profile/change_avatar/', login_required(ProfileViews.AvatarManaging.as_view())),
    path('accounts/profile/like_marks/', login_required(PostViews.PostUrLikes.as_view())),

    path('friends/<int:user_id>/', login_required(FriendsViews.FriendsList.as_view())),
    path('friends/requests/', login_required(FriendsViews.FriendsRequests.as_view())),
    path('friends/<int:user_id>/blacklist/', login_required(FriendsViews.FriendsBlacklist.as_view())),

    path('friends/send_request/<int:user_id>/', login_required(FriendsViews.SendFriendshipRequest.as_view())),
    path('friends/accept_request/<int:user_id>/', login_required(FriendsViews.AcceptRequest.as_view())),
    path('friends/cancel_request/<int:user_id>/', login_required(FriendsViews.cancel_request)),
    path('friends/remove_friend/<int:user_id>/', login_required(FriendsViews.remove_friend)),
    path('friends/add_blacklist/<int:user_id>/', login_required(FriendsViews.blacklist_add)),
    path('friends/remove_blacklist/<int:user_id>/', login_required(FriendsViews.blacklist_remove)),

    path('community/<int:community_id>/', login_required(Communities.CommunityView.as_view())),
    path('community/list/<int:user_id>/', login_required(Communities.CommunityList.as_view())),
    path('community/mylist/', login_required(Communities.my_communities)),
    path('community/create/', login_required(Communities.CommunityCreate.as_view())),
    path('community/<int:community_id>/join/', login_required(Communities.community_join)),
    path('community/<int:community_id>/leave/', login_required(Communities.community_leave)),
    path('community/<int:community_id>/change_avatar/', login_required(Communities.AvatarManaging.as_view())),
    path('community/<int:community_id>/edit/', login_required(Communities.EditCommunity.as_view())),

    path('post/create/', login_required(PostViews.post_new)),
    path('post/create/<int:community_id>/', login_required(Communities.post_community_new)),
    
    path('post/<int:post_id>/', login_required(PostViews.PostView.as_view())),
    path('post/<int:post_id>/ajax/', login_required(PostViews.PostAjax.as_view())),
    path('post/<int:post_id>/remove/', login_required(PostViews.post_remove)),
    path('post/<int:post_id>/edit/', login_required(PostViews.post_edit)),
    path('post/<int:post_id>/send_comment/', login_required(PostViews.send_comment)),

    path('music/<int:user_id>/', login_required(MusicViews.MusicList.as_view())),
    path('music/upload/',  login_required(MusicViews.MusicUpload.as_view())),

    path('ajax/search/', login_required(GlobalSearch.as_view())),
    path('ajax/set_online/', login_required(ProfileViews.set_online)),
    path('ajax/update_nav/', login_required(Index.update_nav)),

    path('like/<int:post_id>/', login_required(PostViews.like_post)),
    
    path('chats/<int:user_id>/', login_required(Conversations.ChatList.as_view())),
    path('chat/create/', login_required(Conversations.create_chat)),
    path('chat/<int:room_id>/remove/', login_required(Conversations.remove_chat)),
    path('chat/quit/<int:room_id>/', login_required(Conversations.quit_room)),
    path('chat/<int:room_id>/add/<int:friend_id>/', login_required(Conversations.add_to_chat)),
    path('chat/<int:room_id>/remove/<int:participant_id>/', login_required(Conversations.remove_from_chat)),
    path('chat/<int:room_id>/makeadmin/<int:participant_id>/', login_required(Conversations.make_admin)),
    path('chat/<int:room_id>/rmadmin/<int:participant_id>/', login_required(Conversations.rm_admin)),
    path('chat/change_avatar/<int:room_id>/', login_required(Conversations.AvatarManaging.as_view())),
    path('chat/edit_chat_name/<int:room_id>/', login_required(Conversations.edit_chat_name)),
    path('chats/<int:user_id>/<int:friend_id>/', login_required(Conversations.chat_move)),
    path('chat/go_to_chat/<int:room_id>/', login_required(Conversations.Room.as_view())),
    path('chat/go_to_chat/<int:room_id>/get_messages/', login_required(Conversations.get_messages)),

    path('files/<int:user_id>/', login_required(Files.all_files))
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
