from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('cat/', cat, name='catalog'),
]