from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect


@login_required
def index(request):
    context = {}

    return render(request, 'index.html', context)
