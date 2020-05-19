"""
Meta social community views
"""

from io import BytesIO
from PIL import Image
from simple_search import search_filter

from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.forms import modelformset_factory
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from core.views import MetaSocialView
from core.forms import CropAvatarForm
from post.forms import PostImageForm, PostForm
from post.models import PostImages

from .models import Community
from .forms import EditCommunityForm, CommunityCreateForm, UpdateCommunityAvatarForm
from user_profile.models import Profile


class Communities:
    """
    Communities class
    """

    class CommunityView(MetaSocialView):
        """
        Community view
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'community/community_page.html'

        def get(self, request, community_url):
            """
            Processing get request
            """
            context = self.get_menu_context('community', 'Сообщество')

            context['community'] = get_object_or_404(Community, custom_url=community_url)

            post_image_form_set = modelformset_factory(PostImages, form=PostImageForm, extra=10, max_num=10)

            context['postform'] = PostForm()
            context['formset'] = post_image_form_set(queryset=PostImages.objects.none())

            context['action_type'] = '/post/create/{}/'.format(community_url)

            return render(request, self.template_name, context)

    class EditCommunity(MetaSocialView):
        """
        Edit community information view
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'community/edit_community.html'
            self.context = self.get_menu_context('community', 'Редактирование сообщества')

        def post(self, request, **kwargs):
            """
            Changing community data (name, info, country)
            """
            community = get_object_or_404(Community, custom_url=kwargs['community_url'])
            self.context['community'] = community
            form = EditCommunityForm(request.POST, instance=self.context['community'])
            if form.is_valid():
                form.save()
                return redirect('/community/{}/'.format(community.custom_url))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            self.context['community'] = get_object_or_404(Community, custom_url=kwargs['community_url'])
            self.context['form'] = EditCommunityForm(instance=self.context['community'])

            return render(request, self.template_name, self.context)

    class CommunityCreate(MetaSocialView):
        """
        Community create view
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'community/community_create.html'

        @staticmethod
        def post(request):
            """
            Creates community
            """
            form = CommunityCreateForm(request.POST)
            if form.is_valid():
                community = Community(
                    name=request.POST.get('name'),
                    info=request.POST.get('info'),
                    country=request.POST.get('country'),
                    owner=request.user,
                    custom_url=request.POST.get('name'),
                )
                community.save()
                community.users.add(request.user)
                request.user.profile.communities.add(community)
                community.admins.add(request.user)
                return redirect('/community/{}/'.format(community.custom_url))

        def get(self, request):
            """
            Processing get request
            """
            context = self.get_menu_context('community', 'Создание сообщества')
            context['form'] = CommunityCreateForm()
            context['community_pages'] = 'create'
            return render(request, self.template_name, context)

    class AvatarManaging(MetaSocialView):
        """
        Managing avatar of community view
        """

        def __init__(self, **kwargs):
            self.context = self.get_menu_context('community', 'Смена аватарки сообщества')
            self.template_name = 'community/change_avatar.html'
            super().__init__(**kwargs)

        def post(self, request, **kwargs):
            """
            Crop and save avatar of community
            """
            community = get_object_or_404(Community, custom_url=kwargs['community_url'])
            avatar_form = UpdateCommunityAvatarForm(request.POST, request.FILES, instance=community)
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
                    image = Image.open(community.base_image)
                cropped_image = image.crop((x, y, w + x, h + y))
                resized_image = cropped_image.resize((256, 256), Image.ANTIALIAS)

                io = BytesIO()

                resized_image.save(io, 'JPEG', quality=60)

                community.image.save('image_{}.jpg'.format(community.id), ContentFile(io.getvalue()),
                                     save=False)
                community.save()

                return redirect('/community/' + str(community.custom_url))

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            avatar_form = UpdateCommunityAvatarForm()
            crop_form = CropAvatarForm()

            self.context['avatar_form'] = avatar_form
            self.context['crop_form'] = crop_form
            self.context['community'] = get_object_or_404(Community, custom_url=kwargs['community_url'])

            return render(request, self.template_name, self.context)

    @staticmethod
    def my_communities(request):
        """
        Method for getting all created communities. Returns rendered responce
        """
        return render(request, 'community/own_community_list.html', {
            'community_pages': 'created'
        })

    class CommunityList(MetaSocialView):
        """
        Community list view
        """

        def __init__(self, **kwargs):
            self.context = {}
            self.template_name_get = 'community/community_list.html'
            self.template_name_post = 'community/search.html'
            super().__init__(**kwargs)

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            self.context = self.get_menu_context('community', 'Список сообществ')

            requested = request.GET.get('username')

            c_user = None
            if requested:
                c_user = get_object_or_404(User,
                                           profile=Profile.objects.get(custom_url=requested))
            else:
                c_user = request.user

            self.context['c_user'] = c_user
            self.context['community_pages'] = 'subs'

            self.pagination_elemetns(
                request,
                list(c_user.profile.communities.all()),
                self.context,
                'c_user_communities'
            )

            return render(request, 'community/community_list.html', self.context)

        def post(self, request, **kwargs):
            """
            Searching communities by name and returns rendered responce
            """

            c_user = request.user

            self.context['matching'] = True
            if not request.POST.get('query'):
                self.context['matching'] = False
                self.context['c_user_communities'] = c_user.profile.communities.all()
                return render(request, 'community/search.html', self.context)
            query = request.POST.get('query')
            search_fields = ['name']
            self.context['c_matches'] = Community.objects.filter(search_filter(search_fields, query))

            return render(request, 'community/search.html', self.context)

    @staticmethod
    def community_join(request, community_url):
        """
        Method for joining to community
        """
        community = get_object_or_404(Community, custom_url=community_url)
        if request.user not in community.users.all():
            community.users.add(request.user)
            request.user.profile.communities.add(community)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def community_leave(request, community_url):
        """
        Mthod for leaving from community
        """
        community = get_object_or_404(Community, custom_url=community_url)
        if request.user in community.users.all():
            community.users.remove(request.user)
            request.user.profile.communities.remove(community)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def post_community_new(request, community_url):
        """
        Function for creating post
        :param community_url: url
        :param request: request
        :return: HttpResponseRedirect
        """

        community = get_object_or_404(Community, custom_url=community_url)

        post_image_form_set = modelformset_factory(PostImages, form=PostImageForm, extra=10, max_num=10)

        if request.method == "POST":
            postForm = PostForm(request.POST)
            formset = post_image_form_set(request.POST, request.FILES, queryset=PostImages.objects.none())

            if postForm.is_valid() and formset.is_valid():
                post_form = postForm.save(commit=False)
                post_form.community = community
                post_form.save()

                for form in formset.cleaned_data:
                    if form:
                        image = form['image']
                        photo = PostImages(post=post_form, image=image, from_user_id=request.user.id)
                        photo.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
