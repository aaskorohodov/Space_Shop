from .models import *


class CardMixin:
    def readcart(self, session):
        try:
            cart_items = session['items']
            print(cart_items)
        except:
            print('No items')

    def add_to_cart(self, session):
        pass