from .views import RegisterView, ad_list, AdCreateView
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', ad_list, name='ad_list'),
    path('create/', AdCreateView.as_view(), name='ad_create')
]