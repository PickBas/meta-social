"""
Meta social music views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from core.views import MetaSocialView
from simple_search import search_filter

from .forms import UploadMusicForm
from user_profile.models import Profile
from user_profile.models import PlayPosition
from music.models import Music


class MusicViews:
    """
    Class containing music functionality and representation
    """

    class MusicList(MetaSocialView):
        """
        Music list representaion
        """

        def __init__(self, **kwargs: dict) -> None:
            """
            MusicList ctor
            :param kwargs: kwargs
            """
            super().__init__(**kwargs)
            self.template_name = 'music/music_list.html'

        def get(self, request, custom_url: str) -> render:
            """
            Processing GET request. Rendering music_list page.
            :param custom_url: user's custom url
            :param request: request
            :return: render
            """
            context = self.get_menu_context('music', 'Музыка')
            context['music_pages'] = 'my_list'

            context['c_user'] = get_object_or_404(Profile, custom_url=custom_url).user
            context['music_list'] = context['c_user'].profile.get_music_list()

            return render(request, self.template_name, context)

        def post(self, request, custom_url: str) -> render:
            """
            Processing POST request. Rendering search list.
            :param custom_url: user's custom url
            :param request: request
            :return: render
            """

            c_user = request.user

            context = self.get_menu_context('music', 'Музыка')
            context['matching'] = True
            if not request.POST.get('query'):
                context['matching'] = False
                context['music_list'] = c_user.profile.get_music_list()
                return render(request, 'music/search.html', context)
            query = request.POST.get('query')
            search_fields = ['title', 'artist']
            context['c_matches'] = Music.objects.filter(search_filter(search_fields, query))

            return render(request, 'music/search.html', context)

    class MusicUpload(MetaSocialView):
        """
        Music upload and representation
        """

        def __init__(self, **kwargs: dict) -> None:
            """
            MusicUpload ctor
            :param kwargs: kwargs
            """
            super().__init__(**kwargs)
            self.template_name = 'music/music_upload.html'

        def post(self, request) -> redirect:
            """
            Processing POST request. Save uploaded music
            :param request: request
            :return: redirect
            """
            form = UploadMusicForm(request.POST, request.FILES)
            if form.is_valid():
                music = form.save()
                playpos = PlayPosition(position=music,
                                       plist=request.user.profile)
                playpos.add_order()
                playpos.save()

            return redirect('/accounts/profile/{}/music/'.format(request.user.profile.custom_url))

        def get(self, request) -> render:
            """
            Processing GET request. Rendering music_upload page.
            :param request: request
            :return: render
            """
            context = self.get_menu_context('music', 'Загрузка музыки')
            context['music_pages'] = 'upload'

            context['form'] = UploadMusicForm()

            return render(request, self.template_name, context)

    @staticmethod
    def add_music(request, music_id: int) -> HttpResponse:
        """
        Method for processing the addition of music.
        :param request: request
        :param music_id: int
        :return: HttpResponse
        """
        music_item = get_object_or_404(Music, id=music_id)

        if music_item in request.user.profile.playlist.all():
            return HttpResponse('Success')

        playpos = PlayPosition(
            position=music_item,
            plist=request.user.profile
        )
        playpos.add_order()
        playpos.save()

        return HttpResponse('Success')

    @staticmethod
    def add_music_from_search(request, music_id: int) -> HttpResponse:
        """
        Method for processing the music search.
        :param request: request
        :param music_id: int
        :return: HttpResponseRedirect
        """
        music_item = get_object_or_404(Music, id=music_id)

        if music_item in request.user.profile.playlist.all():
            return HttpResponse('Success')

        playpos = PlayPosition(
            position=music_item,
            plist=request.user.profile
        )

        playpos.add_order()
        playpos.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def remove(request, music_id: int) -> HttpResponseRedirect:
        """
        Method for processing the removal of music.
        :param request:
        :param music_id:
        :return:
        """
        music_item = get_object_or_404(Music, id=music_id)
        request.user.profile.playlist.remove(music_item)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
