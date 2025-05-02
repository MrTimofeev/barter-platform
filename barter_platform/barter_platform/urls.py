from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка Swagger (вынесено в отдельную переменную для читаемости)
swagger_info = openapi.Info(
    title="Barter Platform API",
    default_version='v1',
    description="API для бартерной платформы",
    contact=openapi.Contact(email="your@email.com"),  # Добавьте контакты
)

schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Системные URL
    path('admin/', admin.site.urls),
    
    # Аутентификация
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    
    # Основное приложение
    path('', include('ads.urls')),
    
    # API
    path('api/', include('api.urls')),
    
    # Документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    # Альтернативный JSON-эндпоинт для документации (для интеграций)
    path('swagger.json', schema_view.without_ui(cache_timeout=0), 
         name='schema-json'),
]