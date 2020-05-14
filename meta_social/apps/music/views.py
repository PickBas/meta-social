from django.shortcuts import render


class MusicViews:
    """
    Music views
    """
    class MusicList(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_list.html'

        def get(self, request, **kwargs):
            """
            Processing get request
            """
            context = get_menu_context('music', 'Музыка')

            context['c_user'] = User.objects.get(id=kwargs['user_id'])
            context['music_list'] = User.objects.get(id=kwargs['user_id']).profile.get_music_list()

            return render(request, self.template_name, context)

    class MusicUpload(View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = 'music/music_upload.html'

        @login_required
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
            context = get_menu_context('music', 'Загрузка музыки')

            context['form'] = UploadMusicForm()

            return render(request, self.template_name, context)
