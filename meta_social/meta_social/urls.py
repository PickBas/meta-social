"""meta_social URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as au_views

from meta_social_app import views
from meta_social_app.views import RegisterFormView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('meta_social_app.urls')),
    path('register/', views.RegisterFormView.as_view()),
    path('login/', au_views.LoginView.as_view()),
    path('logout/', au_views.LogoutView.as_view()),
]
