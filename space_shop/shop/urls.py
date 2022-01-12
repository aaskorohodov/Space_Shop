from django.urls import path

from .views import *

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('cat/', ShopCatalog.as_view(), name='catalog'),
    path('cat/<slug:cat_slug>/', ShopCategory.as_view(), name='category'),
    path('test', test, name='test'),
    path('test2', test2, name='test2'),
    path('cat/<slug:cat_slug>/<slug:post_slug>/', ShowProduct.as_view(), name='product'),
    path('basket/<int:prod_id>/', Basket.as_view(), name='basket')
]


# пользователи
urlpatterns += [
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', LoginUser.as_view(), name='login'),
]