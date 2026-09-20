from django.core.exceptions import ValidationError
from wagtail.blocks import CharBlock, ChoiceBlock, IntegerBlock, PageChooserBlock, RichTextBlock, StructBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class LinkBlock(StructBlock):
    label = CharBlock(label="Bezeichnung", max_length=120)
    is_external = ChoiceBlock(
        label="Linktyp",
        choices=[("internal", "Interne Seite"), ("external", "Externe URL")],
        default="internal",
    )
    page = PageChooserBlock(label="Interne Seite", required=False)
    external_url = URLBlock(label="Externe URL", required=False)

    class Meta:
        icon = "link"
        label = "CTA-Link"

    def clean(self, value):
        value = super().clean(value)
        link_type = value.get("is_external")
        if link_type not in {"internal", "external"}:
            raise ValidationError("Der Linktyp muss internal oder external sein.")
        if link_type == "external" and (not value.get("external_url") or value.get("page")):
            raise ValidationError("Externe Links benötigen eine URL und keine interne Seite.")
        if link_type == "internal" and (not value.get("page") or value.get("external_url")):
            raise ValidationError("Interne Links benötigen eine Seite und keine externe URL.")
        return value


class HeroChapterBlock(StructBlock):
    eyebrow = CharBlock(label="Eyebrow", max_length=160, required=False)
    heading = CharBlock(label="Überschrift", max_length=240)
    paragraph = RichTextBlock(label="Text", required=False)
    cta = LinkBlock(label="CTA", required=False)
    start_seconds = IntegerBlock(label="Startsekunde", min_value=0, required=False)
    end_seconds = IntegerBlock(label="Endsekunde", min_value=0, required=False)

    class Meta:
        icon = "time"
        label = "Hero-Kapitel"


class StatBlock(StructBlock):
    value = CharBlock(label="Wert", max_length=80)
    label = CharBlock(label="Bezeichnung", max_length=160)

    class Meta:
        icon = "order"
        label = "Statistik"


class ValueBlock(StructBlock):
    heading = CharBlock(label="Überschrift", max_length=160)
    text = RichTextBlock(label="Text", required=False)

    class Meta:
        icon = "pick"
        label = "Wert"


class RichSectionBlock(StructBlock):
    heading = CharBlock(label="Überschrift", max_length=240, required=False)
    body = RichTextBlock(label="Text", required=False)
    image = ImageChooserBlock(label="Bild", required=False)

    class Meta:
        icon = "doc-full"
        label = "Inhaltsabschnitt"


class TestimonialReferenceBlock(StructBlock):
    testimonial = SnippetChooserBlock("content.Testimonial", label="Referenzstimme")

    class Meta:
        icon = "user"
        label = "Referenzstimme"


class ServiceReferenceBlock(StructBlock):
    service = SnippetChooserBlock("content.Service", label="Leistung")

    class Meta:
        icon = "pick"
        label = "Leistung"


class TeamReferenceBlock(StructBlock):
    team_member = SnippetChooserBlock("content.TeamMember", label="Teammitglied")

    class Meta:
        icon = "user"
        label = "Teammitglied"


class CVPackageBlock(StructBlock):
    name = CharBlock(label="Paketname", max_length=160)
    price_display = CharBlock(label="Preis (Anzeige)", max_length=120)
    experience_range = CharBlock(label="Erfahrungsbereich", max_length=160, required=False)
    audience = CharBlock(label="Zielgruppe", max_length=160, required=False)
    description = RichTextBlock(label="Beschreibung", required=False)
    cta = LinkBlock(label="CTA", required=False)

    class Meta:
        icon = "form"
        label = "CV-Paket"


class ProcessStepBlock(StructBlock):
    heading = CharBlock(label="Überschrift", max_length=160)
    text = RichTextBlock(label="Text", required=False)

    class Meta:
        icon = "list-ol"
        label = "Ablaufschritt"
