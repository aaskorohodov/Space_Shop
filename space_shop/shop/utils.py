from .models import *


basket_menu = {'Мои заказы': 'account',
               'Отмененные заказы': 'canceled',
               'Изменить пароль': 'password_change',
               'Настройки': 'settings'
               }


class CardMixin:
    def get_left_menu(self, cat_selected, context):
        '''Рисует левое меню для раздела аккаунт. Передает шаблону Base, который сравнивает ключ в basket_menu с переданным
        cat_selected, чтобы нарисовать выбранный пункт и другие пункты.'''
        context['basket_menu'] = basket_menu
        context['cat_selected'] = cat_selected

    def make_cart(self, post):
        product_id = post['prod']
        quantity = post['quantity']
        product = Product.objects.filter(pk=product_id)
        context_cart = {product[0]: quantity}
        session_cart = {product_id: quantity}
        return context_cart, session_cart

    def show_price(self, context):
        context_cart = context['cart']
        print(context['cart'])
        prices = {}
        for prod, quant in context_cart.items():
            overall_prod_price = int(prod.price) * int(quant)
            prices[prod] = overall_prod_price

        context['prices'] = prices

        return context

    def show_cart(self, context, session_cart):
        '''Делает словарь для контекста, куда в ключи кладет продукт (объект), а в значения его количество. Данные берет
        из сессии, где они представлены цифрами {id товара: количество}.
        Сначала из словаря сессии делается два списка, затем список ид-продуктов превращается в объекты продукта,
        и все кладется в новый словарь.'''
        products = []
        quantities = []
        for prod, quant in session_cart.items():
            products.append(prod)
            quantities.append(quant)

        context_cart = {}
        counter = 0
        for el in products:
            product = Product.objects.filter(pk=int(el))
            context_cart[product[0]] = quantities[counter]
            counter += 1

        context['cart'] = context_cart
        # context = self.show_price(cart_context, context)
        return context

    def add_to_cart(self, context, session_cart, post):
        prod_id = int(post['prod'])
        quantity = int(post['quantity'])

        # этот товар уже лежит в корзине, плюсуем количество
        if str(prod_id) in session_cart:
            '''При сохранении в сессию, ключи превращаются в строки, поэтому, обращаясь к этому словарю, используем
            строки.'''
            print('6_1')
            session_cart[str(prod_id)] = int(quantity) + int(session_cart[str(prod_id)])
            context = self.show_cart(context, session_cart)
            return context, session_cart

        # добавляем новый товар
        else:
            print('6_2')
            session_cart[prod_id] = quantity
            context = self.show_cart(context, session_cart)
            return context, session_cart

    def get_cats_for_left_menu(self, context):
        cats = Category.objects.all()
        context['cats'] = cats
        return context

    def save_items_clean_cart(self):
        '''Создает записи в модель ItemsOrdered, то есть записывает, какие товары и в каком количестве были заказаны.
        Также чистить корзину (удаляет словарь cart bз сессии). Если в сессии нет словаря cart, то ничего не делает.'''

        if 'cart' in self.request.session:
            user_name = self.request.user

            for prod, quant in self.request.session['cart'].items():
                item = ItemsOrdered()

                item.order = Order.objects.filter(user=user_name, closed=0).last()
                product = Product.objects.filter(pk=int(prod))[0]

                item.product = product
                item.quantity = int(quant)
                item.save()

            del self.request.session['cart']

    def get_items_for_exact_order(self, order, context):
        '''Добывает модель ItemsOrdered для конкретного заказа. Пакует в список, передает список в контекст.'''
        items = ItemsOrdered.objects.filter(order=order.pk)
        context_items = []

        for item in items:
            context_items.append(item)

        context['items'] = context_items

