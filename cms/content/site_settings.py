from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.blocks import BooleanBlock, CharBlock, PageChooserBlock, StructBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock


class NavigationItemBlock(StructBlock):
    label = CharBlock(label="Bezeichnung", max_length=120)
    is_external = BooleanBlock(label="Externer Link", required=False, default=False)
    page = PageChooserBlock(label="Interne Seite", required=False)
    external_url = URLBlock(label="Externe URL", required=False)

    class Meta:
        icon = "link"
        label = "Navigationselement"

    def clean(self, value):
        value = super().clean(value)
        if value.get("is_external"):
            if not value.get("external_url") or value.get("page"):
                raise ValidationError("Externe Navigationselemente benötigen eine URL und keine interne Seite.")
        elif not value.get("page") or value.get("external_url"):
            raise ValidationError("Interne Navigationselemente benötigen eine Seite und keine externe URL.")
        return value


class SocialLinkBlock(StructBlock):
    label = CharBlock(label="Bezeichnung", max_length=80)
    url = URLBlock(label="URL")

    class Meta:
        icon = "link"
        label = "Social-Link"


class OfficeBlock(StructBlock):
    label = CharBlock(label="Bezeichnung", max_length=120)
    street = CharBlock(label="Straße", max_length=160)
    postal_code = CharBlock(label="Postleitzahl", max_length=20)
    city = CharBlock(label="Stadt", max_length=120)
    telephone = CharBlock(label="Telefon", max_length=80, required=False)
    email = CharBlock(label="E-Mail", max_length=254, required=False)
    map_url = URLBlock(label="Karten-URL", required=False)

    class Meta:
        icon = "site"
        label = "Büro"


@register_setting
class KPSettings(BaseSiteSetting):
    site_name = models.CharField("Website-Name", max_length=160, default="KP Personalberatung")
    full_logo = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Logo (vollständig)",
    )
    compact_logo = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Logo (kompakt)",
    )
    mobile_logo = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Logo (mobil)",
    )
    favicon = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Favicon",
    )
    default_social_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Standard-Social-Bild",
    )
    primary_navigation = StreamField([("item", NavigationItemBlock())], blank=True, use_json_field=True)
    footer_navigation = StreamField([("item", NavigationItemBlock())], blank=True, use_json_field=True)
    legal_navigation = StreamField([("item", NavigationItemBlock())], blank=True, use_json_field=True)
    social_links = StreamField([("item", SocialLinkBlock())], blank=True, use_json_field=True)
    default_telephone = models.CharField("Standard-Telefon", max_length=80, blank=True)
    default_email = models.EmailField("Standard-E-Mail", blank=True)
    offices = StreamField([("office", OfficeBlock())], blank=True, use_json_field=True)
    footer_company_text = models.TextField("Unternehmenstext im Footer", blank=True)
    copyright_text = models.CharField("Copyright-Text", max_length=240, blank=True)
    employer_cta_label = models.CharField("CTA Arbeitgeber", max_length=120, blank=True)
    candidate_cta_label = models.CharField("CTA Kandidaten", max_length=120, blank=True)
    calendly_url = models.URLField("Calendly-URL", blank=True)
    cookie_heading = models.CharField("Cookie-Banner Überschrift", max_length=160, blank=True)
    cookie_explanation = models.TextField("Cookie-Banner Erklärung", blank=True)
    cookie_accept_label = models.CharField("Cookie: Akzeptieren", max_length=80, blank=True)
    cookie_reject_label = models.CharField("Cookie: Ablehnen", max_length=80, blank=True)
    cookie_customize_label = models.CharField("Cookie: Anpassen", max_length=80, blank=True)
    cookie_privacy_link_label = models.CharField("Cookie: Datenschutz-Link", max_length=120, blank=True)
    cookie_privacy_page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Datenschutzseite",
    )
    analytics_enabled = models.BooleanField("Analytics aktiviert", default=False)
    organization_legal_name = models.CharField("Organisation: Rechtsname", max_length=200, blank=True)
    organization_address = models.CharField("Organisation: Adresse", max_length=300, blank=True)
    organization_telephone = models.CharField("Organisation: Telefon", max_length=80, blank=True)
    organization_email = models.EmailField("Organisation: E-Mail", blank=True)
    organization_logo = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Organisation: Logo",
    )
    organization_social_profiles = StreamField(
        [("profile", URLBlock(label="Social-Profil"))], blank=True, use_json_field=True,
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("site_name"), FieldPanel("full_logo"), FieldPanel("compact_logo"),
            FieldPanel("mobile_logo"), FieldPanel("favicon"), FieldPanel("default_social_image"),
        ], heading="Marke"),
        MultiFieldPanel([
            FieldPanel("primary_navigation"), FieldPanel("footer_navigation"),
            FieldPanel("legal_navigation"), FieldPanel("social_links"),
        ], heading="Navigation und Social Media"),
        MultiFieldPanel([
            FieldPanel("default_telephone"), FieldPanel("default_email"), FieldPanel("offices"),
            FieldPanel("footer_company_text"), FieldPanel("copyright_text"),
            FieldPanel("employer_cta_label"), FieldPanel("candidate_cta_label"), FieldPanel("calendly_url"),
        ], heading="Kontakt und Footer"),
        MultiFieldPanel([
            FieldPanel("cookie_heading"), FieldPanel("cookie_explanation"),
            FieldPanel("cookie_accept_label"), FieldPanel("cookie_reject_label"),
            FieldPanel("cookie_customize_label"), FieldPanel("cookie_privacy_link_label"),
            FieldPanel("cookie_privacy_page"), FieldPanel("analytics_enabled"),
        ], heading="Cookies und Analytics"),
        MultiFieldPanel([
            FieldPanel("organization_legal_name"), FieldPanel("organization_address"),
            FieldPanel("organization_telephone"), FieldPanel("organization_email"),
            FieldPanel("organization_logo"), FieldPanel("organization_social_profiles"),
        ], heading="Organisation und strukturierte Daten"),
    ]

    class Meta:
        verbose_name = "KP Website-Einstellungen"
