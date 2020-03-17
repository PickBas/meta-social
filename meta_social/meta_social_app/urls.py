from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.conf import settings
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('accounts/profile/<int:user_id>/', profile),
    path('accounts/profile/<int:user_id>/edit_profile/', login_required(EditProfile.as_view())),
    path('accounts/profile/<user_id>/change_avatar/', crop_image, name='crop'),

    path('friends/<int:user_id>/', friends_list),
    path('friends/search/', friends_search),
    path('friends/requests/', friends_requests),
    path('friends/blacklist/', friends_blacklist),

    path('friends/send_request/<int:user_id>/', send_friendship_request),
    path('friends/accept_request/<int:request_id>/', accept_request),
    path('friends/remove_friend/<int:user_id>/', remove_friend),
    path('friends/add_blacklist/<int:user_id>/', blacklist_remove),
    path('friends/remove_blacklist/<int:user_id>/', blacklist_add),

    path('post/create/', post_new),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
