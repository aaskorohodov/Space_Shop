from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls'))
]

if settings.DEBUG:  # в режиме отладки, когда DEBUG == True, добавляем еще 1 маршрут для статических файлов (картинок)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)