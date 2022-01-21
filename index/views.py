import random

from django.urls import reverse
from simple_search import search_filter

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.http import Http404, HttpRequest
from django.contrib.auth.models import User

from post.forms import PostForm, PostImageForm
from post.models import PostImages
from community.models import Community
from music.models import Music

from .models import Developer


class MetaSocialView(View):

    @staticmethod
    def pagination_elements(request,
                            elements,
                            context,
                            context_key: str,
                            page_size=10):
        page = request.GET.get('page', 1)
        paginator = Paginator(elements, page_size)
        try:
            context[context_key] = paginator.page(page)
        except PageNotAnInteger:
            context[context_key] = paginator.page(1)
        except EmptyPage:
            context[context_key] = []

    @staticmethod
    def get_menu_context(page: str, page_name: str) -> dict:
        available_pages = [
            'profile',
            'newsfeed',
            'friends',
            'community',
            'music',
            'messages',
            'post',
            'like_marks',
            'files',
        ]
        if page not in available_pages:
            raise KeyError
        context = {
            'page': page,
            'pagename': page_name,
        }
        return context


class Index(MetaSocialView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'index.html'

    def get(self, request) -> render:
        context = self.get_menu_context('newsfeed', 'Главная')
        context['pagename'] = "Главная"
        post_image_form_set = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10
        )
        context['postform'] = PostForm()
        context['formset'] = post_image_form_set(queryset=PostImages.objects.none())
        context['action_type'] = reverse('profile-post-create')
        self.pagination_elements(
            request,
            request.user.profile.get_newsfeed(),
            context,
            'newsfeed'
        )
        return render(request, self.template_name, context)

    @staticmethod
    def update_nav(request) -> render:
        if request.method != 'POST':
            raise Http404()
        context = {
            'page': 'friends'
        }
        return render(request, 'navigation_menu.html', context)


class GlobalSearch(View):

    def __init__(self, **kwargs):
        self.template_name = 'search_list.html'
        super().__init__(**kwargs)

    def post(self, request):
        if request.POST.get('query'):
            context = {}
            query = request.POST.get('query')
            search_fields = ['username', 'first_name', 'last_name']
            context['users'] = User.objects.filter(
                search_filter(search_fields, query)
            ).exclude(id=request.user.id)
            search_fields = ['artist', 'title']
            context['music'] = Music.objects.filter(
                search_filter(search_fields, query)
            )
            search_fields = ['name']
            context['communities'] = Community.objects.filter(
                search_filter(search_fields, query)
            )
            return render(request, self.template_name, context)

    def get(self, request):
        raise Http404()


class AboutView(MetaSocialView):

    def __init__(self, **kwargs):
        self.template_name = 'about_us.html'
        super().__init__(**kwargs)
        self.context = self.get_menu_context('post', 'О нас')

    @staticmethod
    def validate_commits(request):
        for i in request.POST:
            if i != 'commits':
                if not request.POST[i].strip():
                    return redirect(reverse('about'))
            else:
                if int(request.POST[i]) < 1 or int(request.POST[i]) > 500:
                    return redirect(reverse('about'))

    def post(self, request):
        CHOICES = [
            'aqua-gradient',
            'purple-gradient',
            'peach-gradient',
            'blue-gradient'
        ]
        commits_validation = self.validate_commits(request)
        if commits_validation is not None:
            return commits_validation
        Developer(
            user=request.user,
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            phrase=request.POST.get('phrase'),
            commits=request.POST.get('commits'),
            task_list=request.POST.get('tasklist'),
            gradient=random.choice(CHOICES)
        ).save()
        return redirect(reverse('about'))

    def get(self, request):
        self.context['devs'] = Developer.objects.all()
        return render(request, self.template_name, self.context)

    @staticmethod
    def remove_developer(request, dev_id):
        dev = get_object_or_404(Developer, id=dev_id)
        if request.user == dev.user:
            dev.delete()
        return redirect(reverse('about'))
