from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import *


def index(request):
    return render(request, 'shop/base.html')

# def cat(request):
#     return render(request, 'shop/catalog.html')


class ShopCatalog(ListView):
    model = Product
    template_name = 'shop/catalog.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.all()
        context['cats'] = cats
        return context


class ShopCategory(ListView):
    model = Product
    template_name = 'shop/catalog.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.all()
        context['cats'] = cats
        return context

    def get_queryset(self):
        return Product.objects.filter(cat__slug=self.kwargs['cat_slug'])


def test(request):
    return render(request, 'shop/test.html')


def test2(request):
    return render(request, 'shop/test2.html')


class ShowPost(DetailView):
    model = Product
    template_name = 'shop/post.html'
    slug_url_kwarg = 'post_slug'  # по умолчанию ищет в urls.py переменную slug, переопределяем ее на другое имя
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = ProductPhoto.objects.all()
        context['photos'] = photos
        return context