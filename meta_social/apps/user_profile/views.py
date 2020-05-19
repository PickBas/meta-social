"""
Meta social user profile views
"""

from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile
from django.shortcuts import render, HttpResponse, redirect
from django.http import Http404
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.utils import timezone

from core.views import MetaSocialView
from core.forms import CropAvatarForm
from post.models import PostImages
from post.forms import PostImageForm, PostForm

from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, UpdateAvatarForm


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
            :param user_id: id
            :return: context
            """
            if not User.objects.filter(id=kwargs['user_id']).exists():
                raise Http404()

            context = self.get_menu_context('profile', 'Профиль')
            context['profile'] = Profile.objects.get(user=kwargs['user_id'])
            user_item = User.objects.get(id=kwargs['user_id'])
            context['c_user'] = user_item

            PostImageFormSet = modelformset_factory(
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
            context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())

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

        def post(self, request, **kwargs) -> redirect:
            """
            Processing post request
            :param request: request
            :param kwargs: attrs
            :return:
            """

            self.previous_birth = User.objects.get(
                id=kwargs['user_id']).profile.birth
            user_form = UserUpdateForm(
                request.POST, instance=User.objects.get(id=kwargs['user_id']))
            self.profile = Profile.objects.get(user=kwargs['user_id'])

            self.profile.show_email = False if request.POST.get(
                'show_email') is None else True

            profile_form = ProfileUpdateForm(request.POST,
                                             instance=self.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()

                if self.profile.birth is None:
                    self.profile.birth = self.previous_birth
                    self.profile.save()

                return redirect('/accounts/profile/' + str(kwargs['user_id']))

        def get(self, request, **kwargs) -> render:
            """
            Processing get request
            :param request: request
            :param kwargs: attrs
            :return: render
            """
            context = self.get_menu_context('profile', 'Редактирование профиля')
            context['profile'] = Profile.objects.get(user=kwargs['user_id'])
            context['uedit'] = User.objects.get(id=kwargs['user_id'])
            context['user_form'] = UserUpdateForm(
                instance=User.objects.get(id=kwargs['user_id'])
            )
            context['profile_form'] = ProfileUpdateForm(
                instance=Profile.objects.get(user=kwargs['user_id']))
            self.previous_birth = User.objects.get(
                id=kwargs['user_id']).profile.birth

            return render(request, self.template_name, context)

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
                    request.user.profile.image.save('image_{}.jpg'.format(request.user.id), ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()
                except OSError:
                    resized_image.save(io, 'PNG', quality=100)
                    request.user.profile.image.save('image_{}.png'.format(request.user.id), ContentFile(io.getvalue()),
                                                    save=False)
                    request.user.profile.save()

                return redirect('/accounts/profile/' + str(request.user.id))

        def get(self, request):
            """
            Processing get request
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
        """
        if request.method == 'POST':
            request.user.profile.last_act = timezone.now()
            request.user.profile.save()
            return HttpResponse('Success')

        raise Http404()


class Files:
    """
    Representation of all uploaded files
    """
    @staticmethod
    def all_files(request, user_id):
        """
        My files view
        """
        context = MetaSocialView.get_menu_context('files', 'Мои файлы')
        all_images_from_posts = PostImages.objects.filter(from_user_id=user_id)
        context['images'] = all_images_from_posts
        return render(request, 'files/files.html', context)
