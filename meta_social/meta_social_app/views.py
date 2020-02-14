from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

from .forms import SignUpForm
from .models import VK_Token
import vk


def get_token_link():
    base = 'https://oauth.vk.com/authorize'
    client_id = '7317110'
    redirect_uri = 'http://localhost:8000/get_token/'
    display = 'page'
    scope = ','.join([
        'friends',
        'stories',
        'wall',
        'groups',
        'offline',
    ])
    response_type = 'token'

    link = base + '?client_id={}&redirect_uri={}&display={}&scope={}&response_type={}'.format(
        client_id, redirect_uri, display, scope, response_type
    )
    return link


@login_required
def get_token_page(request):
    if request.method == 'POST':
        if not VK_Token.objects.filter(user=request.user).exists():
            item = VK_Token(
                access_token=request.POST['token'],
                userpage_id=request.POST['user_id'],
                user=request.user
            )
            item.save()

        return redirect('/')

    return render(request, 'get_token_page.html')


@login_required
def index(request):
    context = {}
    context['l'] = get_token_link()

    if VK_Token.objects.filter(user=request.user).exists():
        vk_data = {}

        user_object = VK_Token.objects.get(user=request.user)
        session = vk.Session(user_object.access_token)
        api = vk.API(session, v='5.103')

        vk_data['user_data'] = api.users.get(user_ids=user_object.userpage_id, fields=['photo_id'])[0]
        vk_data['photo'] = api.photos.get(album_id='profile')['items'][0]['sizes'][3]['url']

        context['vk_data'] = vk_data

    return render(request, 'index.html', context)


class RegisterFormView(FormView):
    form_class = SignUpForm
    # Ссылка, на которую будет перенаправляться user
    # в случае успешной регистрации
    success_url = "#"

    # Шаблон, который будет использоваться при отображении представления.
    template_name = "registration/register.html"

    def form_valid(self, form):
        # Создаём пользователя, если данные в форму были введены корректно.
        form.save()
        for key in form.fields:
            print(form.fields[key])

        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)
