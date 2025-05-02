from django.urls import path
from .views import AdListCreateView, AdDetailView, ProposalListCreateView, ProposalDetailView


urlpatterns = [
    # Эндпоинты для объявлений
    path('ads/', AdListCreateView.as_view(), name='api-ads-list'),
    path('ads/<int:pk>/', AdDetailView.as_view(), name='api-ads-detail'),
    
    # Эндпоинты для предложений обмена
    path('proposals/', ProposalListCreateView.as_view(), name='api-proposals-list'),
    path('proposals/<int:pk>/', ProposalDetailView.as_view(), name='api-proposals-detail'),
]