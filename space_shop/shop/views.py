from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.views.generic.edit import FormMixin

from .forms import *
from .models import *
from .utils import *


class Index(TemplateView):
    template_name = 'shop/home.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.all()
        context['cats'] = cats

        return context


class ShopCatalog(ListView):
    '''Каталог, все категории'''
    model = Category
    template_name = 'shop/catalog.html'
    context_object_name = 'cats'


class ShopCategory(ListView):
    '''Конкретная категория'''
    model = Product
    template_name = 'shop/category.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        for post in context['posts']:
            comments = Comments.objects.filter(product=post.pk)

            overall_rating = 0
            times_rated = 0
            for el in comments:
                try:
                    r = int(el.rating)
                    overall_rating += r
                    times_rated += 1
                except:
                    pass

            try:
                post.overall_rating = range(round(overall_rating / times_rated))
            except:
                pass

        cats = Category.objects.all()
        context['cats'] = cats

        cat = Category.objects.filter(slug=self.kwargs['cat_slug'])
        context['cat'] = cat[0]

        context['cat_selected'] = self.kwargs['cat_slug']

        return context

    def get_queryset(self):
        return Product.objects.filter(cat__slug=self.kwargs['cat_slug'])


class ShowProduct(CardMixin, FormMixin, DetailView):
    '''FormMixin нужен, чтобы в этом типе view можно было ставить форму.'''

    form_class = AddComment
    model = Product
    template_name = 'shop/product.html'
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):
        '''Нужен, так как в урле используется два слага (категория + товар). Ниже мы пытаемся найти товар по его слагу,
        а вторым запросом просто проверяем, существует ли категория, равная второму слагу. Если не указать второй запрос,
        то можно будет в урл вбить любую биллиберду вместо категории, но при правильно указанном товаре, получим страницу.
        Например /asdasdasd/tovar1. А так не получим, будет 404, потому что по слагу asdasdasd нет категории.'''

        try:
            return Product.objects.get(slug=self.kwargs.get('post_slug'), cat__slug=self.kwargs.get('cat_slug'))
        except:
            raise Http404

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            self.request.session['visits']
        except KeyError:
            self.request.session['visits'] = 0

        self.request.session['visits'] = self.request.session['visits'] + 1
        # self.request.session['cart']['test'] = 123
        # print(self.request.session['cart']['test'])

        context['visits'] = self.request.session['visits']
        # print(self.request.session['cart'])

        # self.request.session['items'] = {'1': 1, '2': 2}
        # self.readcart(self.request.session)

        # try:
        #     self.request.session['123']
        # except:
        #     self.request.session['123'] = 'item'
        #
        # context['session'] = self.request.session['123']

        photos = ProductPhoto.objects.filter(product__slug=self.kwargs['post_slug'])
        context['photos'] = photos

        cats = Category.objects.all()
        context['cats'] = cats

        context['cat_selected'] = self.kwargs['cat_slug']

        first_photo = photos[0]
        context['first_photo'] = first_photo

        comments = Comments.objects.filter(product__slug=self.kwargs['post_slug'])
        context['comments'] = comments

        for el in context['comments']:
            try:
                r = int(el.rating)
                el.star_rating = range(r)
            except:
                pass

        overall_rating = 0
        times_rated = 0
        for el in comments:
            try:
                r = int(el.rating)
                overall_rating += r
                times_rated += 1
            except:
                pass

        try:
            context['rating'] = round((overall_rating / times_rated), 1)
        except:
            pass

        values = PropValue.objects.filter(product=context['post'].pk)
        context['values'] = values

        return context

    def get_success_url(self):
        '''Куда направится, в случае успеха.
        reverse_lazy при попытке обратиться к post, потребует в урле post_slug (название товара). Передаем его,
        добывая из текущего объекта модели.'''

        return reverse_lazy('product', kwargs={'post_slug': self.get_object().slug, 'cat_slug': self.get_object().cat.slug})

    def post(self, request, *args, **kwargs):
        '''Переопределяем метод post, который работает с post запросами. В этом типе представления по дефолту нет
        обработки post, так что тут лишь описывается, что если post поступил, то вызови метод form_valid (он ниже).
        Нет нужды прописывать else, так как если форма заполнена неверно, то нажать на кнопку добавить нельзя,
        там вылезет сообщение пользователю.'''

        form = self.get_form()
        if form.is_valid():
            print('Valid')
            return self.form_valid(form)
        else:
            print('Not valid')

    def form_valid(self, form):
        '''Модель состоит из нескольких полей, но пользователь заполняет только часть. Остальные надо заполнить.
        Тут мы берем форму, но не сохраняем в базу. Затем заполняем нужные поля, затем сохраняем.'''

        self.object = form.save(commit=False)
        self.object.product = self.get_object()

        # если пришла пустая строка, то username не введен, возьмем username из системы авторизации
        if self.object.user == "":
            if self.request.user.get_username() == "":
                self.object.user = 'Аноним'
            else:
                self.object.user = self.request.user.get_username()

        self.object.save()
        return super().form_valid(form)


class Basket(CreateView):
    template_name = 'shop/basket.html'
    form_class = MakeOrder

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        # del self.request.session['cart']
        # self.request.session['cart'] = {}
        # print(self.request.session['cart'])

        try:
            cart = self.request.session['cart']
            prod = str(self.kwargs['prod_id'])
        except KeyError:
            self.request.session['cart'] = {}
            cart = self.request.session['cart']
            prod = str(self.kwargs['prod_id'])


        '''Проверяем, не лежит ли товар уже в сессии (в ключах словаря cart). Если уже лежит, то в значение плюсуем
        текущее запрошенное количество товара. Т.е. у корзине лежит 5 союзов, заказали еще 5, стало 10.'''
        if prod in cart.keys():
            cart[prod] = cart[prod] + int(self.request.POST['quantity'])
        else:
            cart[prod] = int(self.request.POST['quantity'])

        self.request.session['cart'] = cart
        self.request.session.modified = True

        print(self.request.session['cart'])

        products = []
        quantities = []
        for prod, quant in cart.items():
            products.append(prod)
            quantities.append(quant)

        cart_context = {}
        counter = 0
        for el in products:
            product = Product.objects.filter(pk=int(el))
            cart_context[product[0]] = quantities[counter]
            counter += 1

        context['cart'] = cart_context
        print(context['cart'])

        return context



class RegisterUser(CreateView):
    '''Регистрация нового пользователя'''
    form_class = RegisterUserForm  # связанный класс формы
    template_name = 'shop/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        '''Вызывается, в случае успешной регистрации. Делает автоматическую авторизацию свежим пользователем.'''
        user = form.save()
        login(self.request, user)
        return redirect('home')


def logout_user(request):
    '''Функция, которую вызывает кнопка Выйти. Делает logout и редирект.'''
    logout(request)
    return redirect('home')


class LoginUser (LoginView):
    '''Авторизация пользователя'''
    form_class = LoginUserForm  # связанный класс формы
    template_name = 'shop/login.html'

    def get_success_url(self):
        '''Куда отправиться, в случае успеха'''
        return reverse_lazy('home')


def test(request, test):
    print(test)
    return render(request, 'shop/test.html')


def test2(request):
    return render(request, 'shop/test2.html')