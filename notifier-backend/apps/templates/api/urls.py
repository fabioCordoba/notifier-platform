from django.urls import path
from .views import TemplateListCreateView, TemplateDetailView

urlpatterns = [
    path('', TemplateListCreateView.as_view(), name='template-list'),
    path('<uuid:pk>/', TemplateDetailView.as_view(), name='template-detail'),
]
