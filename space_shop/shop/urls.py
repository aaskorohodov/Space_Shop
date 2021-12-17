from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('cat/', ShopCatalog.as_view(), name='catalog'),
    path('cat/<slug:cat_slug>/', ShopCategory.as_view(), name='category'),
    path('test', test, name='test'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('test2', test2, name='test2'),
]