from django.contrib import auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.views.generic.edit import FormMixin, FormView
from django.contrib.auth.models import User

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
        '''get_object отличается от get_queryset тем, что возвращает конкретный объект, а не набор объектов.
        Нужен, так как в урле используется два слага (категория + товар). Ниже мы пытаемся найти товар по его слагу,
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
        context['visits'] = self.request.session['visits']

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


class Basket(CardMixin, CreateView):
    template_name = 'shop/basket.html'
    form_class = MakeOrder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = self.get_cats_for_left_menu(context)

        # не передается продукт для добавления в корзину (переход в корзину по ссылке)
        if 'prod' not in self.request.POST:
            print('1')

            # в сессии нет корзины или словарь пуст
            if 'cart' not in self.request.session or not self.request.session['cart']:
                print('2')

            # словарь корзины в сессии имеет товары
            else:
                session_cart = self.request.session['cart']

                # запрос на удаление товара
                if 'del-item' in self.request.POST:
                    try:
                        del session_cart[self.request.POST['del-item']]
                        self.request.session['cart'] = session_cart
                        self.request.session.modified = True
                        context = self.show_cart(context, session_cart)

                    # на всякий случай
                    except:
                        self.show_cart(context, session_cart)

                # запрос на изменение количества товара
                elif 're-quantity' in self.request.POST:
                    prod_id = self.request.POST['re-quantity-prod-id']
                    new_quantity = self.request.POST['re-quantity']
                    session_cart[str(prod_id)] = str(new_quantity)
                    context = self.show_cart(context, session_cart)
                    self.request.session['cart'] = session_cart
                    self.request.session.modified = True

                # запрос на просто показать карзину
                else:
                    print('3')
                    context = self.show_cart(context, session_cart)

        # был передан продукт для добавления
        else:
            print('4')
            # корзина пуста
            if 'cart' not in self.request.session or not self.request.session['cart']:
                print('5')
                context_cart, session_cart = self.make_cart(self.request.POST)
                context['cart'] = context_cart

            # в корзине что-то есть
            else:
                print('6')
                context, session_cart = self.add_to_cart(context, self.request.session['cart'], self.request.POST)

            # кладем корзину в сессию, принудительно сохраняем сессию, передаем контекст в шаблон
            self.request.session['cart'] = session_cart
            self.request.session.modified = True

        try:
            print('show_price try started')
            context = self.show_price(context)
            print('show_price try done')
            return context
        except:
            print('show_price except happened')
            return context

    def form_valid(self, form):

        current_form = form.save(commit=False)
        current_form.user = self.request.user.username
        current_form.save()

        return super().form_valid(form)


class Account(CardMixin, TemplateView):
    template_name = 'shop/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Готовит левое меню для раздела аккаунт, кладет в контекст. Ждет выбранный пункт в меню (Мои заказы)
        self.get_left_menu('Мои заказы', context)

        # Готовим открытые и закрытые заказы, на основе user_name
        user_name = self.request.user
        activ_orders = Order.objects.filter(user=user_name, closed=0)
        context['activ_orders'] = activ_orders

        # Готовим товары для заказов (это другая модель) и кладем в контекст
        for order in context['activ_orders']:
            items = ItemsOrdered.objects.filter(order=order.pk)

            # try на случай, если нет товаров, чтобы обращение по индексу items[0] не вернуло ошибку
            try:
                order.first = items[0]
                # считаем количество товаров, чтобы показать пользователю. Если 1 товар, то шаблон ничего не получит
                if items.count() > 1:
                    order.itemnumber = f'+ {items.count() - 1} позиций'

            except:
                order.first = 'Нет товаров'

        return context

    def post(self, request, *args, **kwargs):
        '''Обработка post-запроса на удаление заказа. Пост выполняется из другого view (MyOrder), и обрабатывается тут.
        Post передает номер заказа на удаление.
        Этот метод должен что-то вернуть, раз мы его переписываем. Он возвращает render, которому отдает все наобходимое,
        в том числе контекст, который подготавливается вызовом метода выше.
        *важно сначала удалить запись, а потом вызвать конструктор контекста, чтобы удаленная запись не попала в конектст.'''

        order_pk = self.request.POST['order-pk']
        del_order = Order.objects.get(pk=order_pk)
        del_order.closed = True
        del_order.save()

        context = self.get_context_data()

        return render(request, 'shop/account.html', context=context)


class CanceledOrders(CardMixin, ListView):
    template_name = 'shop/account.html'
    model = Order
    context_object_name = 'closed_orders'

    def get_queryset(self):
        user_name = self.request.user
        return Order.objects.filter(user=user_name, closed=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.get_left_menu('Отмененные заказы', context)

        for order in context['closed_orders']:
            items = ItemsOrdered.objects.filter(order=order.pk)

            try:
                order.first = items[0]
                # Считаем количество товаров, чтобы показать пользователю. Если 1 товар, то шаблон ничего не получит
                if items.count() > 1:
                    order.itemnumber = f'+ {items.count() - 1} позиций'

            except:
                order.first = 'Нет товаров'

        return context


class MyOrder(CardMixin, DetailView):
    model = Order
    template_name = 'shop/order.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        print(context['order'])
        self.get_items_for_exact_order(context['order'], context)
        self.save_items_clean_cart()

        return context

    def post(self, request, *args, **kwargs):
        """
        *Метод post вызывается только если отправить форму (изменить данные заказа)
        Изменяет комментарий к заказу. При обычной работе, метод get_context_data (в django, а не кастомный), получает
        объект (поскольку это DetailView, то объект = конкретная запись из БД, а не queryset). Чтение записи делается
        другим методом (вроде get_object), который вызывается методом get (вероятно). Тут же мы обрабатываем post,
        который сами и написали, следовательно, get_object не вызывается, get_context не получает свой объект, не может
        записать его в context['object'], вываливается ошибка. Объект записывается как атрибут класса self.object,
        откуда get_context и пытается получить свой объект. Устраняем ошибку, вручную получая объект."""

        order = Order.objects.get(pk=kwargs['pk'])
        self.object = order

        # Записываем новый комментарий, который нам дает форма по ключу comment-remade
        new_comment = self.request.POST['comment-remade']
        order.order_comment = new_comment
        order.save()

        # Зовем конструктор контекста
        context = self.get_context_data()

        # Вручную вызываем рендер, передаем ему все нужное, в том числе контекст
        return render(request, 'shop/order.html', context=context)


class ChangePass(CardMixin, FormView):
    """Занимается сменой пароля. При первом вызове (переход в смену пароля) пропускает метод post, при попутке смены
    пароля, метод post отрабатывает, так как форма переадресует запрос на тот же УРЛ."""
    form_class = ChangePass
    template_name = 'shop/password_change.html'

    def get_context_data(self, old_pass_error=None, new_pass_error=None, done=None, *args, **kwargs):
        """Переменные error и done передает метод post (он ниже). Если он их передал, значит при обработке формы
        случилась ошибка. Тогда эти переменные будут сложены в контекст."""
        context = super().get_context_data(**kwargs)

        # Готовит левое меню для раздела аккаунт, кладет в контекст. Ждет выбранный пункт в меню (Мои заказы)
        self.get_left_menu('Изменить пароль', context)

        '''Ниже готовится форма, которая будет передана в шаблон в контексте. Форма вызывается обращением
        к атрибуту form_class, который был задан первой строчкой в этом классе. Это единственный известный мне способ
        вызвать форму таким образом, положить ее в контекст и отрисовать в шаблоне стандартным способом.'''
        form = self.form_class()
        context['form'] = form

        if old_pass_error is not None:
            context['old_pass_error'] = old_pass_error

        if new_pass_error is not None:
            context['new_pass_error'] = new_pass_error

        if done is not None:
            context['done'] = done

        return context


    def post(self, request, *args, **kwargs):
        """Включается, только если была отправлена форма. Проверяет верно ли введен старый пароль и совпадают ли новые.
        Затем меняет пароль. Проверка на старый пароль происходит попыткой авторизовать пользователя предоставленным
        паролем. Если авторизация не прошла (неверный пароль), то authenticate() вернет None."""

        old_password = self.request.POST['old_password']
        new_password = self.request.POST['new_password']
        new_password2 = self.request.POST['new_password2']
        current_user = self.request.POST['user']

        user = authenticate(username=current_user, password=old_password)

        if user is None and new_password != new_password2:
            context = self.get_context_data(old_pass_error='Старый пароль введен неверно',
                                            new_pass_error='Поля нового пароля не совпадают')

        elif user is None:
            context = self.get_context_data(old_pass_error='Старый пароль введен неверно')

        elif new_password != new_password2:
            context = self.get_context_data(new_pass_error='Поля нового пароля не совпадают')


        if user is not None and new_password == new_password2:
            context = self.get_context_data(done='Готово!')

            u = User.objects.get(username=current_user)
            u.set_password(new_password)
            u.save()

        return render(request, 'shop/password_change.html', context)


class Contact(TemplateView):
    template_name = 'shop/contact.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        cats = Category.objects.all()
        context['cats'] = cats

        return context

class Settings(CardMixin, FormView):
    template_name = 'shop/settings.html'
    form_class = AddUserPhoto

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        self.get_left_menu('Настройки', context)

        form = self.form_class()
        context['form'] = form

        return context

    def post(self, request, *args, **kwargs):
        print(self.request.POST)

        user = User.objects.filter(username=self.request.POST['user'])
        user_pk = user[0].pk

        user_photo = UserExtra()
        user_photo.user_photo = self.request.POST['user_photo']

        context = self.get_context_data()

        return render(request, 'shop/settings.html', context)




class RegisterUser(CreateView):
    '''Регистрация нового пользователя'''
    form_class = RegisterUserForm
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


class LoginUser(LoginView):
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