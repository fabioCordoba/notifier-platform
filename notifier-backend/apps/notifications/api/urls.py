from django.urls import path
from .views import (
    NotificationListView,
    NotificationSendView,
    NotificationDetailView,
    NotificationRetryView,
    NotificationCancelView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('send/', NotificationSendView.as_view(), name='notification-send'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:pk>/retry/', NotificationRetryView.as_view(), name='notification-retry'),
    path('<uuid:pk>/cancel/', NotificationCancelView.as_view(), name='notification-cancel'),
]
