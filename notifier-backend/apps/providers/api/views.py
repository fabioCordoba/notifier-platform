from rest_framework import generics
from ..models import Provider
from ..serializers import ProviderSerializer


class ProviderListCreateView(generics.ListCreateAPIView):
    serializer_class = ProviderSerializer

    def get_queryset(self):
        return Provider.objects.filter(organization=self.request.user)


class ProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProviderSerializer

    def get_queryset(self):
        return Provider.objects.filter(organization=self.request.user)
