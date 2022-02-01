from django.contrib.auth import views
from django.urls import path

from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('cat/', ShopCatalog.as_view(), name='catalog'),
    path('cat/<slug:cat_slug>/', ShopCategory.as_view(), name='category'),
    path('test', test, name='test'),
    path('test2', test2, name='test2'),
    path('cat/<slug:cat_slug>/<slug:post_slug>/', ShowProduct.as_view(), name='product'),
    path('basket', Basket.as_view(), name='basket'),
    path('basket/<int:someint>', Basket.as_view(), name='basket'),
    path('account/<slug:name>/', Account.as_view(), name='account'),
    path('account/<slug:name>/order<int:pk>', MyOrder.as_view(), name='orders'),
    path('account/<slug:name>/canceled', CanceledOrders.as_view(), name='canceled'),
    path('account/<slug:name>/password-change', ChangePass.as_view(), name='password_change'),
    path('contact/', Contact.as_view(), name='contact'),
    path('account/<slug:name>/settings', Settings.as_view(), name='settings')
]

# пользователи
urlpatterns += [
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
]