"""
View module
"""
import json

from django.contrib.auth.models import User

from django.http import Http404, HttpResponse

from simple_search import search_filter

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views import View
from django.utils import timezone
from .models import Profile, Comment, Community, Like

from django.forms import modelformset_factory

from .models import Post, FriendshipRequest, PostImages, Music
from .forms import ProfileUpdateForm, UserUpdateForm, PostForm, PostImageForm, UploadMusicForm, CropAvatarForm, \
    UpdateAvatarForm, CommunityCreateForm, UpdateCommunityAvatarForm, EditCommunityForm, EditPostImageForm
    
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile



