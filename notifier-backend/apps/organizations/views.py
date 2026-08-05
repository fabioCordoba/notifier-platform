from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OrganizationSerializer


class OrganizationMeView(APIView):
    def get(self, request):
        serializer = OrganizationSerializer(request.user)
        return Response(serializer.data)
