from django.urls import path
from .views import ApiKeyCreateView, ApiKeyRevokeView, ApiKeyListView

urlpatterns = [
    path('api-keys/', ApiKeyListView.as_view(), name='api-key-list'),
    path('api-keys/create/', ApiKeyCreateView.as_view(), name='api-key-create'),
    path('api-keys/<uuid:pk>/revoke/', ApiKeyRevokeView.as_view(), name='api-key-revoke'),
]
