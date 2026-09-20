from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string


def validate_https_absolute_url(value: str) -> None:
    """Require canonical overrides to be absolute HTTPS URLs."""
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValidationError("Die kanonische URL muss eine vollständige HTTPS-URL sein.")


def validate_seo_lengths(seo_title: str, search_description: str) -> None:
    errors = {}
    if seo_title and len(seo_title) > 60:
        errors["seo_title"] = "Der SEO-Titel darf höchstens 60 Zeichen enthalten."
    if search_description and len(search_description) > 160:
        errors["search_description"] = "Die Meta-Beschreibung darf höchstens 160 Zeichen enthalten."
    if errors:
        raise ValidationError(errors)


class SEOFieldsMixin(models.Model):
    """Reusable editable SEO fields for every public Wagtail page type."""

    og_title = models.CharField("Open-Graph-Titel", max_length=60, blank=True)
    og_description = models.CharField("Open-Graph-Beschreibung", max_length=160, blank=True)
    og_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Open-Graph-Bild",
    )
    canonical_url = models.URLField(
        "Kanonische URL",
        max_length=300,
        blank=True,
        validators=[validate_https_absolute_url],
        help_text="Optional. Muss eine vollständige HTTPS-URL sein.",
    )
    noindex = models.BooleanField("Nicht indexieren", default=False)
    navigation_label = models.CharField(
        "Navigationsbezeichnung",
        max_length=120,
        blank=True,
        help_text="Optionaler kurzer Name für Navigation und Breadcrumbs.",
    )
    last_reviewed = models.DateField(
        "Zuletzt geprüft am",
        null=True,
        blank=True,
        help_text="Für rechtliche Seiten das Datum der letzten inhaltlichen Prüfung.",
    )

    panels = [
        FieldPanel("seo_title"),
        FieldPanel("search_description"),
        FieldPanel("og_title"),
        FieldPanel("og_description"),
        FieldPanel("og_image"),
        FieldPanel("canonical_url"),
        FieldPanel("noindex"),
        FieldPanel("navigation_label"),
        FieldPanel("last_reviewed"),
    ]

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        validate_seo_lengths(self.seo_title, self.search_description)
