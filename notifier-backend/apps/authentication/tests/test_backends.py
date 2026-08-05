import pytest
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed
from apps.organizations.models import Organization, ApiKey
from apps.authentication.backends import ApiKeyAuthentication


@pytest.mark.django_db
class TestApiKeyAuthentication:
    def setup_method(self):
        self.factory = RequestFactory()
        self.backend = ApiKeyAuthentication()
        self.org = Organization.objects.create(name="Auth Test Org")
        self.key_instance, self.raw_key = ApiKey.generate(self.org, "Test Key")

    def _make_request(self, header=None):
        request = self.factory.get("/api/v1/notifications/")
        if header:
            request.META["HTTP_AUTHORIZATION"] = header
        return request

    def test_valid_api_key_returns_organization(self):
        request = self._make_request(f"Api-Key {self.raw_key}")
        result = self.backend.authenticate(request)
        assert result is not None
        user, auth = result
        assert user.id == self.org.id
        assert auth.id == self.key_instance.id

    def test_no_header_returns_none(self):
        request = self._make_request()
        result = self.backend.authenticate(request)
        assert result is None

    def test_wrong_keyword_returns_none(self):
        request = self._make_request(f"Bearer {self.raw_key}")
        result = self.backend.authenticate(request)
        assert result is None

    def test_invalid_key_raises_authentication_failed(self):
        request = self._make_request("Api-Key ntf_invalidkeyxyz")
        with pytest.raises(AuthenticationFailed):
            self.backend.authenticate(request)

    def test_inactive_key_raises_authentication_failed(self):
        self.key_instance.is_active = False
        self.key_instance.save()
        request = self._make_request(f"Api-Key {self.raw_key}")
        with pytest.raises(AuthenticationFailed):
            self.backend.authenticate(request)

    def test_authenticate_header_returns_keyword(self):
        request = self._make_request()
        assert self.backend.authenticate_header(request) == "Api-Key"
