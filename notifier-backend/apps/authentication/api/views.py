from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.organizations.models import ApiKey
from ..serializers import ApiKeyCreateSerializer


class ApiKeyCreateView(APIView):
    def post(self, request):
        serializer = ApiKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = request.user
        api_key_instance, raw_key = ApiKey.generate(
            organization=organization,
            name=serializer.validated_data['name'],
        )
        return Response({
            'id': str(api_key_instance.id),
            'name': api_key_instance.name,
            'key': raw_key,
            'prefix': api_key_instance.key_prefix,
            'created_at': api_key_instance.created_at,
        }, status=status.HTTP_201_CREATED)


class ApiKeyRevokeView(APIView):
    def delete(self, request, pk):
        api_key = get_object_or_404(ApiKey, id=pk, organization=request.user)
        api_key.is_active = False
        api_key.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiKeyListView(APIView):
    def get(self, request):
        keys = ApiKey.objects.filter(
            organization=request.user,
            is_active=True,
        ).values('id', 'name', 'key_prefix', 'created_at', 'last_used_at', 'expires_at')
        return Response(list(keys))
