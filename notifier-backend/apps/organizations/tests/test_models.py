import pytest
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization, ApiKey


@pytest.mark.django_db
class TestOrganizationModel:
    def test_create_organization(self):
        org = Organization.objects.create(name="Acme Corp")
        assert str(org) == "Acme Corp"
        assert org.is_active is True
        assert org.plan == Organization.Plan.FREE

    def test_organization_str(self):
        org = Organization(name="Test Org")
        assert str(org) == "Test Org"


@pytest.mark.django_db
class TestApiKeyModel:
    def setup_method(self):
        self.org = Organization.objects.create(name="Test Org")

    def test_generate_returns_instance_and_raw_key(self):
        instance, raw_key = ApiKey.generate(self.org, "My Key")
        assert raw_key.startswith("ntf_")
        assert instance.key_prefix == raw_key[:12]
        assert instance.organization == self.org
        assert instance.is_active is True

    def test_raw_key_is_hashed_in_db(self):
        import hashlib
        instance, raw_key = ApiKey.generate(self.org, "Hashed Key")
        expected_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        assert instance.key_hash == expected_hash

    def test_authenticate_valid_key(self):
        instance, raw_key = ApiKey.generate(self.org, "Auth Key")
        result = ApiKey.authenticate(raw_key)
        assert result is not None
        assert result.id == instance.id

    def test_authenticate_invalid_key(self):
        result = ApiKey.authenticate("ntf_invalidkey123")
        assert result is None

    def test_authenticate_inactive_key(self):
        instance, raw_key = ApiKey.generate(self.org, "Inactive Key")
        instance.is_active = False
        instance.save()
        result = ApiKey.authenticate(raw_key)
        assert result is None

    def test_authenticate_expired_key(self):
        instance, raw_key = ApiKey.generate(self.org, "Expired Key")
        instance.expires_at = timezone.now() - timedelta(hours=1)
        instance.save()
        result = ApiKey.authenticate(raw_key)
        assert result is None

    def test_authenticate_updates_last_used_at(self):
        instance, raw_key = ApiKey.generate(self.org, "Track Key")
        assert instance.last_used_at is None
        ApiKey.authenticate(raw_key)
        instance.refresh_from_db()
        assert instance.last_used_at is not None

    def test_str_representation(self):
        instance, raw_key = ApiKey.generate(self.org, "Str Key")
        assert "ntf_" in str(instance)
        assert "Test Org" in str(instance)
