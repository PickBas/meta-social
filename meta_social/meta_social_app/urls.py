from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.conf import settings
from .views import *


urlpatterns = [
    path('', login_required(Index.as_view()), name='home'),
    path('track/logout/<int:user_id>/', logout_track),
    path('accounts/profile/<int:user_id>/', login_required(ProfileViews.ProfilePage.as_view())),
    path('accounts/profile/<int:user_id>/edit_profile/', login_required(ProfileViews.EditProfile.as_view())),
    path('accounts/profile/change_avatar/', login_required(ProfileViews.AvatarManaging.as_view())),

    path('friends/<int:user_id>/', friends_list),
    path('friends/requests/', friends_requests),
    path('friends/<int:user_id>/blacklist/', friends_blacklist),

    path('friends/send_request/<int:user_id>/', send_friendship_request),
    path('friends/accept_request/<int:user_id>/', accept_request),
    path('friends/cancel_request/<int:user_id>/', cancel_request),
    path('friends/remove_friend/<int:user_id>/', remove_friend),
    path('friends/add_blacklist/<int:user_id>/', blacklist_add),
    path('friends/remove_blacklist/<int:user_id>/', blacklist_remove),

    path('community/<int:community_id>/', community),
    path('community/list/<int:user_id>/', community_list),
    path('community/create/', community_create),
    path('community/<int:community_id>/join/', community_join),
    path('community/<int:community_id>/leave/', community_leave),

    path('post/create/', login_required(PostViews.post_new)),
    path('post/create/<int:community_id>/', post_community_new),
    
    path('post/<int:post_id>/', login_required(PostViews.PostView.as_view())),
    path('post/<int:post_id>/ajax/', login_required(PostViews.PostAjax.as_view())),
    path('post/<int:post_id>/remove/', login_required(PostViews.post_remove)),
    path('post/<int:post_id>/edit/', login_required(PostViews.post_edit)),

    path('music/<int:user_id>/', login_required(MusicViews.MusicList.as_view())),
    path('music/upload/',  login_required(MusicViews.MusicUpload.as_view())),

    path('ajax/search/', global_search),
    path('like/<int:post_id>/', like_post),
    
    path('chats/<int:user_id>/', login_required(Conversations.ChatList.as_view())),
    path('chats/<int:user_id>/<int:friend_id>/', login_required(Conversations.chat_move)),
    path('chat/go_to_chat/<int:room_id>/', login_required(Conversations.Room.as_view())),
    path('chat/go_to_chat/<int:room_id>/get_messages/', login_required(Conversations.get_messages)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
