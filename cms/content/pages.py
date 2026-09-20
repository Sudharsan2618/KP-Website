from django.db import models
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import CharBlock, RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.documents.blocks import DocumentChooserBlock

from .blocks import (
    LinkBlock,
    CVPackageBlock,
    ProcessStepBlock,
    RichSectionBlock,
    ServiceReferenceBlock,
    StatBlock,
    TeamReferenceBlock,
    TestimonialReferenceBlock,
    ValueBlock,
)
from .page_base import KPPageBase


def validate_job_dates(publication_date, closing_date):
    if closing_date and publication_date and closing_date < publication_date:
        from django.core.exceptions import ValidationError
        raise ValidationError("Das Schließungsdatum darf nicht vor dem Veröffentlichungsdatum liegen.")


class HeroPageMixin(models.Model):
    hero_eyebrow = models.CharField("Hero-Eyebrow", max_length=160, blank=True)
    hero_heading = models.CharField("Hero-Überschrift", max_length=240)
    hero_text = RichTextField("Hero-Text", blank=True)
    hero_background_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Hero-Hintergrundbild",
    )
    hero_background_video = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Hero-Hintergrundvideo",
    )
    hero_ctas = StreamField([("cta", LinkBlock())], blank=True, use_json_field=True)

    hero_panels = [
        FieldPanel("hero_eyebrow"), FieldPanel("hero_heading"), FieldPanel("hero_text"),
        FieldPanel("hero_background_image"), FieldPanel("hero_background_video"), FieldPanel("hero_ctas"),
    ]

    class Meta:
        abstract = True


class EmployerPage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    intro_heading = models.CharField("Intro-Überschrift", max_length=240, blank=True)
    intro_body = RichTextField("Intro-Text", blank=True)
    services_eyebrow = models.CharField("Leistungen-Eyebrow", max_length=160, blank=True)
    services_heading = models.CharField("Leistungen-Überschrift", max_length=240, blank=True)
    services = StreamField([("service", ServiceReferenceBlock())], blank=True, use_json_field=True)
    why_eyebrow = models.CharField("Warum-Kastell-Eyebrow", max_length=160, blank=True)
    why_heading = models.CharField("Warum-Kastell-Überschrift", max_length=240, blank=True)
    why_kastell = StreamField([("section", RichSectionBlock())], blank=True, use_json_field=True)
    statistics = StreamField([("stat", StatBlock())], blank=True, use_json_field=True)
    testimonials_eyebrow = models.CharField("Kundenstimmen-Eyebrow", max_length=160, blank=True)
    show_testimonial_content = models.BooleanField("Kundenstimmen anzeigen", default=False, help_text="Zeigt die Testimonial-Karten unter dem Kundenstimmen-Banner an.")
    testimonials_background_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Kundenstimmen-Hintergrundbild",
    )
    testimonials = StreamField([("testimonial", TestimonialReferenceBlock())], blank=True, use_json_field=True)
    recruitment_region_heading = models.CharField("Regionen-Überschrift", max_length=240, blank=True)
    recruitment_region_copy = RichTextField("Regionen-Text", blank=True)
    recruitment_region_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Regionen-Bild",
    )
    recruitment_regions = StreamField([("region", CharBlock(label="Region", max_length=120))], blank=True, use_json_field=True)
    closing_cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)
    calendly_cta_label = models.CharField("Calendly-CTA", max_length=120, blank=True)
    closing_eyebrow = models.CharField("Abschluss-Eyebrow", max_length=160, blank=True)
    closing_heading = models.CharField("Abschluss-Überschrift", max_length=240, blank=True)
    closing_copy = RichTextField("Abschluss-Text", blank=True)
    closing_background_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Abschluss-Hintergrundbild",
    )

    content_panels = HeroPageMixin.hero_panels + [
        MultiFieldPanel([FieldPanel("intro_heading"), FieldPanel("intro_body")], heading="Intro"),
        MultiFieldPanel([FieldPanel("services_eyebrow"), FieldPanel("services_heading"), FieldPanel("services")], heading="Leistungen"),
        MultiFieldPanel([FieldPanel("why_eyebrow"), FieldPanel("why_heading"), FieldPanel("why_kastell")], heading="Warum Kastell"),
        FieldPanel("statistics"),
        MultiFieldPanel([FieldPanel("testimonials_eyebrow"), FieldPanel("testimonials_background_image"), FieldPanel("show_testimonial_content"), FieldPanel("testimonials")], heading="Kundenstimmen"),
        MultiFieldPanel([
            FieldPanel("recruitment_region_heading"), FieldPanel("recruitment_region_copy"),
            FieldPanel("recruitment_region_image"), FieldPanel("recruitment_regions"),
        ], heading="Rekrutierungsregionen"),
        MultiFieldPanel([
            FieldPanel("closing_eyebrow"), FieldPanel("closing_heading"), FieldPanel("closing_copy"),
            FieldPanel("closing_background_image"), FieldPanel("closing_cta"), FieldPanel("calendly_cta_label"),
        ], heading="Abschluss-CTA"),
    ]

    class Meta:
        verbose_name = "Arbeitgeberseite"


class CandidatePage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    show_hero = models.BooleanField("Hero anzeigen", default=False, help_text="Die Produktionsseite für Kandidat:innen beginnt direkt mit dem Leistungsbereich.")
    services_eyebrow = models.CharField("Leistungen-Eyebrow", max_length=160, blank=True)
    services_heading = models.CharField("Leistungen-Überschrift", max_length=240, blank=True)
    services = StreamField([("service", ServiceReferenceBlock())], blank=True, use_json_field=True)
    testimonials_eyebrow = models.CharField("Kundenstimmen-Eyebrow", max_length=160, blank=True)
    show_testimonial_content = models.BooleanField("Kundenstimmen anzeigen", default=False, help_text="Zeigt die Testimonial-Karten unter dem Kundenstimmen-Banner an.")
    testimonials_background_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="candidate_testimonial_pages")
    testimonials = StreamField([("testimonial", TestimonialReferenceBlock())], blank=True, use_json_field=True)
    career_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="candidate_career_pages")
    career_heading = models.CharField("Karriere-Überschrift", max_length=240, blank=True)
    career_copy = RichTextField("Karriere-Text", blank=True)
    contact_background_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="candidate_contact_pages")
    contact_heading = models.CharField("Kontakt-Überschrift", max_length=240, blank=True)
    closing_cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)
    contact_details = RichTextField("Kontaktangaben", blank=True)

    content_panels = HeroPageMixin.hero_panels + [
        FieldPanel("show_hero"),
        MultiFieldPanel([FieldPanel("services_eyebrow"), FieldPanel("services_heading"), FieldPanel("services")], heading="Leistungen"),
        MultiFieldPanel([FieldPanel("testimonials_eyebrow"), FieldPanel("testimonials_background_image"), FieldPanel("show_testimonial_content"), FieldPanel("testimonials")], heading="Kundenstimmen"),
        MultiFieldPanel([FieldPanel("career_image"), FieldPanel("career_heading"), FieldPanel("career_copy")], heading="Karrierebereich"),
        MultiFieldPanel([FieldPanel("contact_background_image"), FieldPanel("contact_heading"), FieldPanel("contact_details")], heading="Kontaktbereich"),
        FieldPanel("closing_cta"),
    ]

    class Meta:
        verbose_name = "Kandidatenseite"


class AboutPage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    who_we_are_heading = models.CharField("Wer-wir-sind-Überschrift", max_length=240, blank=True)
    who_we_are_sections = StreamField([("section", RichSectionBlock())], blank=True, use_json_field=True)
    statistics = StreamField([("stat", StatBlock())], blank=True, use_json_field=True)
    team_eyebrow = models.CharField("Team-Eyebrow", max_length=160, blank=True)
    team_heading = models.CharField("Team-Überschrift", max_length=240, blank=True)
    team_lead = RichTextField("Team-Einleitung", blank=True)
    team_members = StreamField([("member", TeamReferenceBlock())], blank=True, use_json_field=True)
    values = StreamField([("value", ValueBlock())], blank=True, use_json_field=True)
    contact_cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)

    content_panels = HeroPageMixin.hero_panels + [
        FieldPanel("who_we_are_heading"), FieldPanel("who_we_are_sections"),
        FieldPanel("statistics"), MultiFieldPanel([FieldPanel("team_eyebrow"), FieldPanel("team_heading"), FieldPanel("team_lead"), FieldPanel("team_members")], heading="Beraterteam"), FieldPanel("values"),
        FieldPanel("contact_cta"),
    ]

    class Meta:
        verbose_name = "Über-uns-Seite"


class ServicePage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    SERVICE_CHOICES = [
        ("eignungsdiagnostik", "Eignungsdiagnostik"),
        ("internationale-rekrutierung", "Internationale Rekrutierung"),
        ("volumen-projektbesetzung", "Volumen- & Projektbesetzung"),
        ("employer-branding", "Employer Branding"),
    ]
    service_key = models.CharField("Service-Schlüssel", max_length=80, choices=SERVICE_CHOICES, unique=True)
    intro = RichTextField("Intro", blank=True)
    body_sections = StreamField([("section", RichSectionBlock())], blank=True, use_json_field=True)
    cta_heading = models.CharField("CTA-Überschrift", max_length=240, blank=True)
    cta_text = RichTextField("CTA-Text", blank=True)
    cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)
    show_calendly_cta = models.BooleanField("Calendly-CTA anzeigen", default=False)

    content_panels = HeroPageMixin.hero_panels + [
        FieldPanel("service_key"), FieldPanel("intro"), FieldPanel("body_sections"),
        MultiFieldPanel([
            FieldPanel("cta_heading"), FieldPanel("cta_text"), FieldPanel("cta"),
            FieldPanel("show_calendly_cta"),
        ], heading="Abschluss-CTA"),
    ]

    class Meta:
        verbose_name = "Leistungsseite"
        verbose_name_plural = "Leistungsseiten"


class CVPackagesPage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    intro = RichTextField("Intro", blank=True)
    packages = StreamField([("package", CVPackageBlock())], blank=True, use_json_field=True)
    how_it_works_heading = models.CharField("So funktioniert es: Überschrift", max_length=240, blank=True)
    how_it_works_intro = RichTextField("So funktioniert es: Intro", blank=True)
    how_it_works_steps = StreamField([("step", ProcessStepBlock())], blank=True, use_json_field=True)
    delivery_time_text = models.CharField("Lieferzeit", max_length=240, blank=True)

    content_panels = HeroPageMixin.hero_panels + [
        FieldPanel("intro"), FieldPanel("packages"),
        MultiFieldPanel([
            FieldPanel("how_it_works_heading"), FieldPanel("how_it_works_intro"),
            FieldPanel("how_it_works_steps"), FieldPanel("delivery_time_text"),
        ], heading="Ablauf"),
    ]

    class Meta:
        verbose_name = "Bewerbungsunterlagen-Seite"


class ContactPage(HeroPageMixin, KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    page_heading = models.CharField("Seitenüberschrift", max_length=240)
    introduction = RichTextField("Einleitung", blank=True)
    office_labels = StreamField(
        [("office", CharBlock(label="Büro-Bezeichnung", max_length=120))],
        blank=True,
        use_json_field=True,
        help_text="Geordnete Bezeichnungen aus den Büros in KPSettings.",
    )
    website_url_label = models.CharField("Website-URL-Bezeichnung", max_length=120, blank=True)
    website_url = models.URLField("Website-URL", blank=True)
    closing_copy = RichTextField("Abschlusstext", blank=True)

    content_panels = HeroPageMixin.hero_panels + [
        FieldPanel("page_heading"), FieldPanel("introduction"), FieldPanel("office_labels"),
        FieldPanel("website_url_label"), FieldPanel("website_url"), FieldPanel("closing_copy"),
    ]

    class Meta:
        verbose_name = "Kontaktseite"


class LegalPage(KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    intro = RichTextField("Einleitung", blank=True)
    body = RichTextField("Rechtlicher Inhalt", blank=True)

    content_panels = [FieldPanel("intro"), FieldPanel("body"), FieldPanel("last_reviewed")]

    class Meta:
        verbose_name = "Rechtliche Seite"
        verbose_name_plural = "Rechtliche Seiten"


class JobsIndexPage(KPPageBase):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["content.JobPage"]
    hero_eyebrow = models.CharField("Hero-Eyebrow", max_length=160, blank=True)
    hero_heading = models.CharField("Hero-Überschrift", max_length=240)
    hero_intro = RichTextField("Hero-Intro", blank=True)
    search_label = models.CharField("Suchfeld-Bezeichnung", max_length=160, blank=True)
    search_placeholder = models.CharField("Suchfeld-Platzhalter", max_length=160, blank=True)
    filter_heading = models.CharField("Filter-Überschrift", max_length=160, blank=True)
    location_filter_label = models.CharField("Filter: Standort", max_length=120, blank=True)
    category_filter_label = models.CharField("Filter: Kategorie", max_length=120, blank=True)
    remote_filter_label = models.CharField("Filter: Remote", max_length=120, blank=True)
    empty_state_text = models.CharField("Leerzustand", max_length=240, blank=True)
    result_count_format = models.CharField("Ergebniszählung", max_length=160, blank=True)
    application_note = RichTextField("Bewerbungshinweis", blank=True)
    default_application_email = models.EmailField("Standard-Bewerbungs-E-Mail", blank=True)

    content_panels = [
        FieldPanel("hero_eyebrow"), FieldPanel("hero_heading"), FieldPanel("hero_intro"),
        MultiFieldPanel([
            FieldPanel("search_label"), FieldPanel("search_placeholder"), FieldPanel("filter_heading"),
            FieldPanel("location_filter_label"), FieldPanel("category_filter_label"),
            FieldPanel("remote_filter_label"), FieldPanel("empty_state_text"), FieldPanel("result_count_format"),
        ], heading="Suche und Filter"),
        FieldPanel("application_note"), FieldPanel("default_application_email"),
    ]

    class Meta:
        verbose_name = "Projektstellen-Übersicht"


class JobPage(KPPageBase):
    parent_page_types = ["content.JobsIndexPage"]
    subpage_types = []
    STATUS_CHOICES = [
        ("draft", "Entwurf"),
        ("open", "Offen"),
        ("filled", "Besetzt"),
        ("archived", "Archiviert"),
    ]
    source_key = models.CharField("Quellschlüssel", max_length=160, unique=True)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="draft")
    publication_date = models.DateField("Veröffentlichungsdatum", default=timezone.now)
    closing_date = models.DateField("Schließungsdatum", null=True, blank=True)
    location_display = models.CharField("Standortanzeige", max_length=200, blank=True)
    remote = models.BooleanField("Remote möglich", default=False)
    category = models.CharField("Kategorie", max_length=160, blank=True)
    specialization = models.CharField("Spezialisierung / Modul", max_length=200, blank=True)
    experience_display = models.CharField("Erfahrung (Anzeige)", max_length=160, blank=True)
    employment_type = models.CharField("Beschäftigungsart", max_length=160, blank=True)
    summary = RichTextField("Einleitung / Zusammenfassung", blank=True)
    responsibilities = StreamField([("item", RichTextBlock(label="Aufgabe"))], blank=True, use_json_field=True)
    candidate_profile = StreamField([("item", RichTextBlock(label="Anforderung"))], blank=True, use_json_field=True)
    benefits = StreamField([("item", RichTextBlock(label="Vorteil"))], blank=True, use_json_field=True)
    application_email = models.EmailField("Bewerbungs-E-Mail", blank=True)
    external_ats_identifier = models.CharField("Externe ATS-ID", max_length=160, blank=True)
    external_ats_url = models.URLField("Externe ATS-URL", blank=True)

    content_panels = [
        FieldPanel("source_key"), FieldPanel("status"), FieldPanel("publication_date"),
        FieldPanel("closing_date"), FieldPanel("location_display"), FieldPanel("remote"),
        FieldPanel("category"), FieldPanel("specialization"), FieldPanel("experience_display"),
        FieldPanel("employment_type"), FieldPanel("summary"), FieldPanel("responsibilities"),
        FieldPanel("candidate_profile"), FieldPanel("benefits"), FieldPanel("application_email"),
        MultiFieldPanel([
            FieldPanel("external_ats_identifier"), FieldPanel("external_ats_url"),
        ], heading="ATS (später)"),
    ]

    def clean(self):
        super().clean()
        validate_job_dates(self.publication_date, self.closing_date)

    class Meta:
        verbose_name = "Projektstelle"
        verbose_name_plural = "Projektstellen"
