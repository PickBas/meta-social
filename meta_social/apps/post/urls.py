from django.urls import path

from .views import *


urlpatterns = [
    path('post/create/', login_required(PostViews.post_new)),
    path('post/create/<int:community_id>/', login_required(Communities.post_community_new)),
    
    path('post/<int:post_id>/', login_required(PostViews.PostView.as_view())),
    path('post/<int:post_id>/ajax/', login_required(PostViews.PostAjax.as_view())),
    path('post/<int:post_id>/remove/', login_required(PostViews.post_remove)),
    path('post/<int:post_id>/send_comment/', login_required(PostViews.send_comment)),
    path('post/<int:post_id>/edit/', login_required(PostViews.PostEdit.as_view())),

    path('like/<int:post_id>/', login_required(PostViews.like_post)),
]
