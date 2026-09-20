from datetime import date
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase

from .serializers import PageSerializer, serialize_seo, serialize_value
from .site_settings import serialize_site_settings
from .site_settings_views import site_settings
from .jobs import jobs_list
from .preview import create_preview_token, preview_revision
from .views import page_by_path


class SerializerTests(SimpleTestCase):
    def test_seo_serializer_uses_page_title_as_fallback(self):
        page = SimpleNamespace(
            title="Arbeitgeber", seo_title="", search_description="Beschreibung",
            og_title="", og_description="", og_image=None, canonical_url="",
            noindex=False, navigation_label="", last_reviewed=date(2026, 9, 19),
        )
        result = serialize_seo(page)
        self.assertEqual(result["title"], "Arbeitgeber")
        self.assertEqual(result["canonical_url"], None)
        self.assertEqual(result["last_reviewed"], "2026-09-19")

    def test_nested_values_are_json_safe(self):
        self.assertEqual(serialize_value({"items": [date(2026, 9, 19)]}), {"items": ["2026-09-19"]})

    def test_serializer_returns_version_one_envelope_shape(self):
        class Field:
            def __init__(self, name):
                self.name = name

        page = SimpleNamespace(
            _meta=SimpleNamespace(app_label="content", concrete_fields=[Field("body")]),
            pk=4, title="Test", slug="test", url_path="/test/", body="Hallo",
            latest_revision_created_at=None, last_published_at=None,
            seo_title="", search_description="", og_title="", og_description="",
            og_image=None, canonical_url="", noindex=False, navigation_label="", last_reviewed=None,
        )
        result = PageSerializer(page).data
        self.assertEqual(result["type"], "content.SimpleNamespace")
        self.assertEqual(result["fields"], {"body": "Hallo"})


class PageByPathViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_path_is_bad_request(self):
        response = page_by_path(self.factory.get("/api/v1/pages/by-path/"))
        self.assertEqual(response.status_code, 400)

    def test_unknown_path_is_not_found(self):
        live = Mock()
        live.filter.return_value.select_related.return_value.first.return_value = None
        with patch("content.api.v1.views.Page.objects.live", return_value=live):
            response = page_by_path(self.factory.get("/api/v1/pages/by-path/?path=/unknown/"))
        self.assertEqual(response.status_code, 404)

    def test_published_path_returns_data_envelope(self):
        specific = SimpleNamespace(
            _meta=SimpleNamespace(app_label="content", concrete_fields=[]),
            pk=8, title="Arbeitgeber", slug="arbeitgeber", url_path="/arbeitgeber/",
            latest_revision_created_at=None, last_published_at=None,
            seo_title="", search_description="", og_title="", og_description="",
            og_image=None, canonical_url="", noindex=False, navigation_label="", last_reviewed=None,
        )
        page = SimpleNamespace(specific=specific)
        live = Mock()
        live.filter.return_value.select_related.return_value.first.return_value = page
        with patch("content.api.v1.views.Page.objects.live", return_value=live):
            response = page_by_path(self.factory.get("/api/v1/pages/by-path/?path=/arbeitgeber/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["data"]["url_path"], "/arbeitgeber/")


class SiteSettingsTests(SimpleTestCase):
    def test_serializer_exposes_only_public_fields(self):
        settings = SimpleNamespace(
            site_name="KP", default_email="hallo@example.com", analytics_enabled=False,
            calendly_url="https://calendly.com/kp", database_password="must-not-appear",
        )
        result = serialize_site_settings(settings)
        self.assertEqual(result["site_name"], "KP")
        self.assertNotIn("database_password", result)

    def test_site_settings_endpoint_returns_data(self):
        settings = SimpleNamespace(site_name="KP", analytics_enabled=False)
        request = RequestFactory().get("/api/v1/site-settings/")
        with patch("content.api.v1.site_settings_views.KPSettings.for_request", return_value=settings):
            response = site_settings(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["data"]["site_name"], "KP")


class JobsEndpointTests(SimpleTestCase):
    def test_invalid_remote_filter_is_bad_request(self):
        response = jobs_list(RequestFactory().get("/api/v1/jobs/?remote=maybe"))
        self.assertEqual(response.status_code, 400)

    def test_invalid_page_is_bad_request(self):
        response = jobs_list(RequestFactory().get("/api/v1/jobs/?page=zero"))
        self.assertEqual(response.status_code, 400)


class PreviewTests(SimpleTestCase):
    def test_preview_token_round_trip_uses_opaque_payload(self):
        with self.settings(PREVIEW_SIGNING_SECRET="preview-test-secret"):
            token = create_preview_token(SimpleNamespace(pk=12), revision_id=34)
        self.assertNotIn("preview-test-secret", token)
        self.assertGreater(len(token), 20)

    def test_invalid_preview_token_is_not_found(self):
        request = RequestFactory().get("/api/v1/preview/not-a-token/")
        with self.settings(PREVIEW_SIGNING_SECRET="preview-test-secret"):
            response = preview_revision(request, "not-a-token")
        self.assertEqual(response.status_code, 404)
