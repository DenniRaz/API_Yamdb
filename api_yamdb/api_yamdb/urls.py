from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# Импорт списка урлов вашего приложения
from api.urls import urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # Подключение списка урлов вашего приложения
    path('api/', include(urlpatterns)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
