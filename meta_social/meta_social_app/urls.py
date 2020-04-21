from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.conf import settings
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('track/logout/<int:user_id>/', logout_track),
    path('accounts/profile/<int:user_id>/', profile),
    path('accounts/profile/<int:user_id>/edit_profile/', login_required(EditProfile.as_view())),
    path('accounts/profile/change_avatar/', change_avatar),

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
    path('community/list/', community_list),
    path('community/create/', community_create),
    path('community/<int:community_id>/join/', community_join),
    path('community/<int:community_id>/leave/', community_leave),

    path('post/create/', post_new),
    path('post/create/<int:community_id>/', post_community_new),
    
    path('post/<int:post_id>/', post_view),
    path('post/<int:post_id>/ajax/', post_ajax),
    path('post/<int:post_id>/remove/', post_remove),
    path('post/<int:post_id>/edit/', post_edit),

    path('music/<int:user_id>/', music_list),
    path('music/upload/', music_upload),

    path('chat/', chat),
    path('chat/go_to_chat/<int:user_id>/', show_messages),
    path('chat/go_to_chat/<int:user_id>/send_mes/', send_message),

    path('ajax/search/', global_search),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
