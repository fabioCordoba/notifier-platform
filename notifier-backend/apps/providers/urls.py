from django.urls import path
from .views import ProviderListCreateView, ProviderDetailView

urlpatterns = [
    path('', ProviderListCreateView.as_view(), name='provider-list'),
    path('<uuid:pk>/', ProviderDetailView.as_view(), name='provider-detail'),
]
