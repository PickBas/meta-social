"""
Meta social music views
"""

from django.shortcuts import render
from django.contrib.auth.models import User

from core.views import MetaSocialView

from .forms import UploadMusicForm


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

            context['c_user'] = User.objects.get(id=kwargs['user_id'])
            context['music_list'] = User.objects.get(id=kwargs['user_id']).profile.get_music_list()

            return render(request, self.template_name, context)

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
                music = form.save(commit=False)
                music.user = request.user
                music.save()

        def get(self, request):
            """
            Processing get request
            """
            context = self.get_menu_context('music', 'Загрузка музыки')

            context['form'] = UploadMusicForm()

            return render(request, self.template_name, context)
