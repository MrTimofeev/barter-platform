from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from ads.models import Ad, ExchangeProposal
from .serializers import AdSerializer, ProposalSerializer

# Для объявлений
class AdListCreateView(ListCreateAPIView):
    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer

class AdDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

# Для предложений обмена
class ProposalListCreateView(ListCreateAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ProposalSerializer

class ProposalDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ProposalSerializer