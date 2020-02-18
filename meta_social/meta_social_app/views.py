from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView

from .forms import SignUpForm
import vk_api


def profile_page(request, user_id):
    if User.objects.filter(id=user_id).exists():
        user_item = User.objects.get(id=user_id)
        context = {'username': user_item.username}
    else:
        raise Http404()

    return render(request, 'profile.html', context)


@login_required
def index(request):
    context = {}

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
