import pytest
from apps.organizations.models import Organization
from apps.templates.models import Template


@pytest.mark.django_db
class TestTemplateModel:
    def setup_method(self):
        self.org = Organization.objects.create(name="Template Test Org")
        self.template = Template.objects.create(
            organization=self.org,
            name="Bienvenida",
            channel=Template.Channel.EMAIL,
            subject="Bienvenido {{nombre}}",
            body="Hola {{nombre}}, gracias por registrarte en {{empresa}}.",
            variables=["nombre", "empresa"],
        )

    def test_render_replaces_all_variables(self):
        result = self.template.render({"nombre": "Fabio", "empresa": "Acme"})
        assert result["subject"] == "Bienvenido Fabio"
        assert "Fabio" in result["body"]
        assert "Acme" in result["body"]

    def test_render_missing_variable_leaves_placeholder(self):
        result = self.template.render({"nombre": "Fabio"})
        assert "{{empresa}}" in result["body"]

    def test_render_empty_variables(self):
        result = self.template.render({})
        assert "{{nombre}}" in result["subject"]
        assert "{{empresa}}" in result["body"]

    def test_render_non_string_variable_is_converted(self):
        result = self.template.render({"nombre": 42, "empresa": "Corp"})
        assert "42" in result["subject"]

    def test_str_representation(self):
        assert str(self.template) == "Bienvenida [EMAIL]"

    def test_unique_together_constraint(self):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Template.objects.create(
                organization=self.org,
                name="Bienvenida",
                channel=Template.Channel.EMAIL,
                body="Duplicate",
            )
