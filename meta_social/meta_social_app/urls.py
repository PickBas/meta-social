from django.urls import path
from .views import *
from django.contrib.auth import views as au_views

urlpatterns = [
    path('', index),
    path('register/', RegisterFormView.as_view()),
    path('login/', au_views.LoginView.as_view()),
    path('logout/', au_views.LogoutView.as_view()),
    path('login/pass-reset/', au_views.PasswordResetView.as_view(template_name='pass_reset.html'), name='pass-reset'),
    path('password_reset_confirm/<uidb64>/<token>/',
         au_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset/done/',
         au_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset_complete/',
         au_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    path('profile/<int:user_id>/', profile_page)
]