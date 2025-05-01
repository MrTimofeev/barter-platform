from .views import *
from django.urls import path

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', AdListView.as_view(), name='ad_list'),
    path('create/', AdCreateView.as_view(), name='ad_create'),
    path('<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('<int:pk>/edit/', AdUpdateView.as_view(), name='ad_edit'),
    path('<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
    path('propose/<int:sender_pk>/to/<int:receiver_pk>/', ExchangeProposalCreateView.as_view(), name='propose_exchange'),
    path('proposal/<int:pk>/update/', ExchangeProposalUpdateView.as_view(), name='update_proposal'),
    path('my-proposals/', MyProposalsView.as_view(), name='my_proposals'),

]
