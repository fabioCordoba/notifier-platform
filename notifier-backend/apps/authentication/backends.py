from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.organizations.models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith(f'{self.keyword} '):
            return None

        raw_key = auth_header[len(self.keyword) + 1:].strip()
        api_key = ApiKey.authenticate(raw_key)

        if api_key is None:
            raise AuthenticationFailed('API key inválida o expirada.')

        return (api_key.organization, api_key)

    def authenticate_header(self, request):
        return self.keyword
