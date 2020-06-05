"""
Meta social user profile views
"""

from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.utils import timezone

from core.views import MetaSocialView
from core.forms import CropAvatarForm
from post.models import PostImages
from post.forms import PostImageForm, PostForm

from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, UpdateAvatarForm
from friends.models import FriendshipRequest
from friends.views import FriendsViews


class ProfileViews:
    """
    ProfileViews
    """

    class ProfilePage(MetaSocialView):
        """
        Profile page view
        """

        def __init__(self, **kwargs):
            self.template_name = 'profile/profile_page.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs) -> render:
            """
            User profile view.

            :param request: request
            :return: context
            """
            if not User.objects.filter(profile=Profile.objects.get(custom_url=kwargs['user_url'])).exists():
                raise Http404()

            context = self.get_menu_context('profile', 'Профиль')
            context['profile'] = Profile.objects.get(custom_url=kwargs['user_url'])
            user_item = User.objects.get(profile=Profile.objects.get(custom_url=kwargs['user_url']))
            context['c_user'] = user_item

            post_image_form_set = modelformset_factory(
                PostImages, form=PostImageForm, extra=10, max_num=10
            )

            pass_add_to_friends = False

            is_in_blacklist = False

            if user_item != request.user:
                if request.user not in user_item.profile.friends.all():
                    pass_add_to_friends = True
                if request.user in user_item.profile.blacklist.all():
                    is_in_blacklist = True

            context['is_in_blacklist'] = is_in_blacklist
            context['is_friend'] = True if request.user in user_item.profile.friends.all() \
                                           and request.user != user_item else False
            context['pass_add_to_friends'] = pass_add_to_friends

            context['postform'] = PostForm()
            context['formset'] = post_image_form_set(queryset=PostImages.objects.none())

            user_item.username

            if not is_in_blacklist:
                self.pagination_elemetns(
                    request,
                    list(reversed(user_item.profile.posts.all())),
                    context,
                    'c_user_posts'
                )

            context['action_type'] = '/post/create/'

            return render(request, self.template_name, context)

    class EditProfile(MetaSocialView):
        """
        EditProfile class
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'profile/edit_profile.html'
            self.profile = None
            self.previous_birth = None

        def get(self, request, **kwargs) -> render:
            """
            Processing get request

            :param request: request
            :param kwargs: attrs
            :return: render
            """
            context = self.get_menu_context('profile', 'Редактирование профиля')
            context['profile'] = Profile.objects.get(custom_url=kwargs['user_url'])
            context['uedit'] = User.objects.get(profile=Profile.objects.get(custom_url=kwargs['user_url']))
            context['user_form'] = UserUpdateForm(
                instance=User.objects.get(profile=Profile.objects.get(custom_url=kwargs['user_url']))
            )
            context['profile_form'] = ProfileUpdateForm(
                instance=Profile.objects.get(custom_url=kwargs['user_url']))
            self.previous_birth = User.objects.get(profile=Profile.objects.get(
                custom_url=kwargs['user_url']
            )).profile.birth

            return render(request, self.template_name, context)

        def post(self, request, **kwargs) -> redirect:
            """
            Processing post request

            :param request: request
            :param kwargs: attrs
            :return:
            """

            self.previous_birth = Profile.objects.get(custom_url=kwargs['user_url']).birth

            user_form = UserUpdateForm(
                request.POST,
                instance=User.objects.get(profile=
                                          Profile.objects.get(custom_url=kwargs['user_url'])))

            self.profile = Profile.objects.get(custom_url=kwargs['user_url'])

            self.profile.show_email = False if request.POST.get(
                'show_email') is None else True

            self.profile.custom_url = kwargs['user_url'] if request.POST.get(
                'custom_url') is None else request.POST.get('custom_url')

            profile_form = ProfileUpdateForm(request.POST,
                                             instance=self.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()

                if self.profile.birth is None:
                    self.profile.birth = self.previous_birth
                    self.profile.save()

                return redirect('/accounts/profile/' + str(self.profile.custom_url) + '/')

            return self.get(request, **kwargs)

    class AvatarManaging(MetaSocialView):
        """
        Profile avatar manage view
        """

        def __init__(self, **kwargs):
            self.context = self.get_menu_context('profile', 'Смена аватарки')
            self.template_name = 'profile/change_avatar.html'
            super().__init__(**kwargs)

        def post(self, request):
            """
            Cropping and saving user avatar

            :param request: request
            :return: redirect
            """
            avatar_form = UpdateAvatarForm(request.POST, request.FILES, instance=request.user.profile)
            crop_form = CropAvatarForm(request.POST)
            if crop_form.is_valid() and avatar_form.is_valid():
                avatar_form.save()

                x = float(request.POST.get('x'))
                y = float(request.POST.get('y'))
                w = float(request.POST.get('width'))
                h = float(request.POST.get('height'))

                if request.FILES.get('base_image'):
                    image = Image.open(request.FILES.get('base_image'))
                else:
                    image = Image.open(request.user.profile.base_image)
                cropped_image = image.crop((x, y, w + x, h + y))
                resized_image = cropped_image.resize((256, 256), Image.ANTIALIAS)

                io = BytesIO()

                try:
                    resized_image.save(io, 'JPEG', quality=100)
                    request.user.profile.image.save('image_{}.jpg'.format(request.user.id),
                                                    ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()
                except OSError:
                    resized_image.save(io, 'PNG', quality=100)
                    request.user.profile.image.save('image_{}.png'.format(request.user.id),
                                                    ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()

                return redirect('/accounts/profile/' + str(request.user.profile.custom_url) + '/')

        def get(self, request):
            """
            Representation of user changing avatar

            :param request: request
            :return: HttpResponce with HTML
            """
            avatar_form = UpdateAvatarForm()
            crop_form = CropAvatarForm()

            self.context['avatar_form'] = avatar_form
            self.context['crop_form'] = crop_form

            return render(request, self.template_name, self.context)

    @staticmethod
    def set_online(request):
        """
        Method for setting last action time in user profile

        :param request: request
        :raises: Http404
        """
        if request.method == 'POST':
            request.user.profile.last_act = timezone.now()
            request.user.profile.save()
            return HttpResponse('Success')

        raise Http404()

    @staticmethod
    def send_friend_request(request, user_id):
        user_item = get_object_or_404(User, id=user_id)

        if not FriendshipRequest.objects.filter(from_user=user_item,
                                                to_user=request.user).exists():
            if not FriendshipRequest.objects.filter(from_user=request.user,
                                                    to_user=user_item).exists():
                item = FriendshipRequest(
                    from_user=request.user,
                    to_user=user_item,
                )

                item.save()

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        raise Http404()


class Files:
    """
    Representation of all uploaded files
    """

    @staticmethod
    def all_files(request, user_url):
        """
        My files view

        :param request: request
        :param user_url: user url
        :return: HttpResponce with HTML
        """
        context = MetaSocialView.get_menu_context('files', 'Мои файлы')
        c_user = User.objects.get(profile=Profile.objects.get(custom_url=user_url))
        all_images_from_posts = PostImages.objects.filter(from_user_id=c_user.id)
        context['images'] = all_images_from_posts
        return render(request, 'files/files.html', context)
