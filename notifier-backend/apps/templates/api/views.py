from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Template
from ..serializers import TemplateSerializer


class TemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = TemplateSerializer

    def get_queryset(self):
        return Template.objects.filter(
            organization=self.request.user, is_active=True
        )


class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TemplateSerializer

    def get_queryset(self):
        return Template.objects.filter(organization=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
