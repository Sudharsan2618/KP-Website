from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet
from wagtail.blocks import CharBlock


@register_snippet
class TeamMember(models.Model):
    source_key = models.CharField("Quellschlüssel", max_length=120, unique=True)
    name = models.CharField("Name", max_length=160)
    role = models.CharField("Rolle", max_length=160, blank=True)
    portrait = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Porträt",
    )
    biography = RichTextField("Biografie", blank=True)
    expertise_tags = StreamField(
        [("tag", CharBlock(label="Expertise", max_length=80))],
        blank=True,
        use_json_field=True,
        verbose_name="Expertise-Tags",
    )
    email = models.EmailField("E-Mail", blank=True)
    telephone = models.CharField("Telefon", max_length=80, blank=True)
    linkedin_url = models.URLField("LinkedIn-URL", blank=True)
    active = models.BooleanField("Aktiv", default=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("source_key"), FieldPanel("name"), FieldPanel("role"),
            FieldPanel("portrait"), FieldPanel("active"),
        ], heading="Stammdaten"),
        FieldPanel("biography"),
        FieldPanel("expertise_tags"),
        MultiFieldPanel([
            FieldPanel("email"), FieldPanel("telephone"), FieldPanel("linkedin_url"),
        ], heading="Kontakt"),
    ]

    class Meta:
        ordering = ["name", "source_key"]
        verbose_name = "Teammitglied"
        verbose_name_plural = "Teammitglieder"

    def __str__(self):
        return self.name


@register_snippet
class Testimonial(models.Model):
    AUDIENCE_CHOICES = [
        ("employer", "Arbeitgeber"),
        ("candidate", "Kandidat"),
    ]

    source_key = models.CharField("Quellschlüssel", max_length=120, unique=True)
    quote = models.TextField("Zitat")
    person_label = models.CharField("Personenbezeichnung", max_length=160, blank=True)
    role = models.CharField("Rolle", max_length=160, blank=True)
    organization = models.CharField("Organisation", max_length=200, blank=True)
    audience = models.CharField("Zielgruppe", max_length=20, choices=AUDIENCE_CHOICES)
    display_order = models.PositiveIntegerField("Anzeigereihenfolge", default=0)
    active = models.BooleanField("Aktiv", default=True)

    panels = [
        FieldPanel("source_key"), FieldPanel("quote"), FieldPanel("person_label"),
        FieldPanel("role"), FieldPanel("organization"), FieldPanel("audience"),
        FieldPanel("display_order"), FieldPanel("active"),
    ]

    class Meta:
        ordering = ["display_order", "source_key"]
        verbose_name = "Referenzstimme"
        verbose_name_plural = "Referenzstimmen"

    def __str__(self):
        return self.person_label or self.source_key


@register_snippet
class Service(models.Model):
    ICON_CHOICES = [
        ("briefcase", "Aktenkoffer"),
        ("chart", "Diagramm"),
        ("globe", "Globus"),
        ("people", "Personen"),
        ("document", "Dokument"),
        ("search", "Suche"),
    ]
    AUDIENCE_CHOICES = [
        ("employer", "Arbeitgeber"),
        ("candidate", "Kandidat"),
        ("both", "Beide"),
    ]

    source_key = models.CharField("Quellschlüssel", max_length=120, unique=True)
    title = models.CharField("Titel", max_length=200)
    short_description = models.TextField("Kurzbeschreibung", blank=True)
    icon_identifier = models.CharField("Icon", max_length=40, choices=ICON_CHOICES)
    detail_page = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Detailseite",
    )
    display_order = models.PositiveIntegerField("Anzeigereihenfolge", default=0)
    audience = models.CharField("Zielgruppe", max_length=20, choices=AUDIENCE_CHOICES)
    active = models.BooleanField("Aktiv", default=True)

    panels = [
        FieldPanel("source_key"), FieldPanel("title"), FieldPanel("short_description"),
        FieldPanel("icon_identifier"), FieldPanel("detail_page"), FieldPanel("display_order"),
        FieldPanel("audience"), FieldPanel("active"),
    ]

    class Meta:
        ordering = ["display_order", "source_key"]
        verbose_name = "Leistung"
        verbose_name_plural = "Leistungen"

    def __str__(self):
        return self.title
