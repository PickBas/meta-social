"""
Meta social core views module
"""

from simple_search import search_filter

from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.http import Http404
from django.contrib.auth.models import User

from post.forms import PostForm, PostImageForm
from post.models import PostImages
from community.models import Community
from music.models import Music


class MetaSocialView(View):
    """
    Base view class with common functional
    """

    @staticmethod
    def pagination_elemetns(request, elements, context, context_key: str, page_size=10):
        """
        elements - query elem for paginate: list
        request
        page => context[context_key]
        """

        page = request.GET.get('page', 1)
        paginator = Paginator(elements, page_size)
        try:
            context[context_key] = paginator.page(page)
        except PageNotAnInteger:
            context[context_key] = paginator.page(1)
        except EmptyPage:
            context[context_key] = []

    @staticmethod
    def get_menu_context(page: str, pagename: str) -> dict:
        """
        Getting context
        :param page: str
        :param pagename: str
        :return: context
        """

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
            'pagename': pagename,
        }

        return context


class Index(MetaSocialView):
    """
    Index Class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'index.html'

    def get(self, request) -> render:
        """
        Index page view
        :param request: request
        :return: render
        """
        context = self.get_menu_context('newsfeed', 'Главная')
        context['pagename'] = "Главная"

        PostImageFormSet = modelformset_factory(
            PostImages, form=PostImageForm, extra=10, max_num=10
        )

        context['postform'] = PostForm()
        context['formset'] = PostImageFormSet(queryset=PostImages.objects.none())
        context['action_type'] = '/post/create/'

        self.pagination_elemetns(
            request,
            request.user.profile.get_newsfeed(),
            context,
            'newsfeed'
        )

        return render(request, self.template_name, context)

    @staticmethod
    def update_nav(request):
        """
        Method for updating navigation menu. Retutns rendered responce
        """
        if request.method == 'POST':
            context = {
                'page': 'friends'
            }

            return render(request, 'navigation_menu.html', context)

        raise Http404()


class GlobalSearch(View):
    """
    Global search view
    """
    def __init__(self, **kwargs):
        self.template_name = 'search_list.html'
        super().__init__(**kwargs)

    def post(self, request):
        """
        Site search. Returns rendered responce
        """
        if request.POST.get('query'):
            context = {}
            query = request.POST.get('query')

            search_fields = ['username', 'first_name', 'last_name']
            context['users'] = User.objects.filter(search_filter(search_fields, query)).exclude(id=request.user.id)

            search_fields = ['artist', 'title']
            context['music'] = Music.objects.filter(search_filter(search_fields, query))

            search_fields = ['name']
            context['communities'] = Community.objects.filter(search_filter(search_fields, query))

            return render(request, self.template_name, context)

    def get(self, request):
        """
        Processing get request
        """
        raise Http404()
