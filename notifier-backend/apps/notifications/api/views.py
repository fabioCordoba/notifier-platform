from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Notification, Recipient
from ..serializers import (
    NotificationSendSerializer,
    NotificationDetailSerializer,
    NotificationListSerializer,
)
from ..tasks import process_notification


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationListSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(organization=self.request.user)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class NotificationSendView(APIView):
    def post(self, request):
        organization = request.user
        serializer = NotificationSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        template = None
        if data.get("template_id"):
            from apps.templates.models import Template
            template = get_object_or_404(Template, id=data["template_id"], organization=organization)

        notification = Notification.objects.create(
            organization=organization,
            title=data["title"],
            message=data.get("message", ""),
            template=template,
            template_variables=data.get("template_variables", {}),
            priority=data["priority"],
            channels=data["channels"],
            metadata=data.get("metadata", {}),
            scheduled_at=data.get("scheduled_at"),
            status=Notification.Status.QUEUED,
        )

        for r in data["recipients"]:
            Recipient.objects.create(notification=notification, **r)

        if not notification.scheduled_at:
            process_notification.delay(str(notification.id))

        return Response(
            NotificationDetailSerializer(notification).data,
            status=status.HTTP_202_ACCEPTED,
        )


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationDetailSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            organization=self.request.user
        ).prefetch_related("recipients__delivery_attempts")


class NotificationRetryView(APIView):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, organization=request.user)
        retryable = (Notification.Status.FAILED, Notification.Status.PARTIALLY_FAILED)
        if notification.status not in retryable:
            return Response(
                {"detail": "Solo se pueden reintentar notificaciones con estado FAILED o PARTIALLY_FAILED."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notification.status = Notification.Status.QUEUED
        notification.save(update_fields=["status", "updated_at"])
        process_notification.delay(str(notification.id))
        return Response({"detail": "Reintento encolado."}, status=status.HTTP_202_ACCEPTED)


class NotificationCancelView(APIView):
    def delete(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, organization=request.user)
        if notification.status != Notification.Status.QUEUED:
            return Response(
                {"detail": "Solo se pueden cancelar notificaciones con estado QUEUED."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notification.status = Notification.Status.CANCELLED
        notification.save(update_fields=["status", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
