from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'shop/base.html')

def cat(request):
    return render(request, 'shop/catalog.html')