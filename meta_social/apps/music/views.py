"""
Meta social music views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from core.views import MetaSocialView

from .forms import UploadMusicForm
from user_profile.models import PlayPosition


class MusicViews:
    """
    Class containing music functionality and representation
    """
    class MusicList(MetaSocialView):
        """
        Music list representaion
        """
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_list.html'

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            context = self.get_menu_context('music', 'Музыка')

            c_user = User.objects.get(id=kwargs['user_id'])
            context['c_user'] = c_user
            context['music_list'] = c_user.profile.get_music_list()
            context['music_pages'] = 'my_list'

            return render(request, self.template_name, context)

        def post(self, request, **kwargs):
            """
            Replace order
            """
            str_arr = request.POST.get('music_order')
            arr = list(map(int, str_arr.split(',')))
            c_user = User.objects.get(id=kwargs['user_id'])
            c_user.profile.change_playlist(arr)
            return render(request, self.template_name, {})


    class MusicUpload(MetaSocialView):
        """
        Music upload and representation
        """
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_upload.html'

        def post(self, request):
            """
            Processing post request. Save uploaded music
            """
            form = UploadMusicForm(request.POST, request.FILES)
            if form.is_valid():
                music = form.save()
                playpos = PlayPosition(position=music,
                                       plist=request.user.profile)
                playpos.add_order()
                playpos.save()
            
            return redirect('/music/{}/'.format(request.user.id))

        def get(self, request):
            """
            Processing get request
            """
            context = self.get_menu_context('music', 'Загрузка музыки')

            context['form'] = UploadMusicForm()
            context['music_pages'] = 'upload'

            return render(request, self.template_name, context)
