import json

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.db import OperationalError
from django.test import RequestFactory, override_settings
from unittest.mock import Mock
from datetime import date

from .blocks import LinkBlock
from .middleware import ApiFailureMiddleware
from .pages import validate_job_dates
from .seo import validate_https_absolute_url, validate_seo_lengths
from .site_settings import NavigationItemBlock


class CanonicalURLValidationTests(SimpleTestCase):
    def test_accepts_absolute_https_url(self):
        validate_https_absolute_url("https://www.kp.example/seite/")

    def test_rejects_relative_url(self):
        with self.assertRaises(ValidationError):
            validate_https_absolute_url("/seite/")

    def test_rejects_non_https_url(self):
        with self.assertRaises(ValidationError):
            validate_https_absolute_url("http://www.kp.example/seite/")

    def test_seo_title_limit_is_validated_without_truncation(self):
        with self.assertRaises(ValidationError):
            validate_seo_lengths("x" * 61, "Kurz")

    def test_search_description_limit_is_validated_without_truncation(self):
        with self.assertRaises(ValidationError):
            validate_seo_lengths("Kurz", "x" * 161)


class NavigationItemValidationTests(SimpleTestCase):
    def test_external_item_requires_external_url(self):
        block = NavigationItemBlock()
        cleaned = block.clean({"label": "Karriere", "is_external": True, "page": None, "external_url": "https://example.com"})
        self.assertEqual(cleaned["external_url"], "https://example.com")

    def test_external_item_cannot_contain_internal_page(self):
        block = NavigationItemBlock()
        with self.assertRaises(ValidationError):
            block.clean({"label": "Karriere", "is_external": True, "page": object(), "external_url": "https://example.com"})


class PageValidationTests(SimpleTestCase):
    def test_job_closing_date_cannot_precede_publication(self):
        with self.assertRaises(ValidationError):
            validate_job_dates(date(2026, 9, 20), date(2026, 9, 19))

    def test_cta_link_type_is_controlled(self):
        block = LinkBlock()
        with self.assertRaises(ValidationError):
            block.clean({"label": "Mehr", "is_external": "unknown", "page": None, "external_url": None})


class ApiFailureMiddlewareTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_database_failure_returns_safe_api_503(self):
        middleware = ApiFailureMiddleware(Mock(side_effect=OperationalError("database unavailable")))
        response = middleware(RequestFactory().get("/api/v1/jobs/"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {"error": "cms_unavailable"})

    @override_settings(DEBUG=False)
    def test_non_api_database_failure_is_not_masked(self):
        middleware = ApiFailureMiddleware(Mock(side_effect=OperationalError("database unavailable")))
        with self.assertRaises(OperationalError):
            middleware(RequestFactory().get("/admin/"))


class CloudinaryConfigurationTests(SimpleTestCase):
    def test_cloudinary_storage_dependency_is_installed(self):
        from cloudinary_storage.storage import MediaCloudinaryStorage

        self.assertIsNotNone(MediaCloudinaryStorage)
