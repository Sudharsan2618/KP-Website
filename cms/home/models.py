from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import CharBlock, RichTextBlock, StreamBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string

from content.blocks import HeroChapterBlock, LinkBlock, RichSectionBlock
from content.page_base import KPPageBase


class HomePage(KPPageBase):
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "content.EmployerPage", "content.CandidatePage", "content.AboutPage",
        "content.ServicePage", "content.CVPackagesPage", "content.ContactPage",
        "content.JobsIndexPage", "content.LegalPage",
    ]
    intro_video = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Intro-Video",
    )
    intro_video_url = models.URLField("Intro-Video-URL (Cloudinary)", blank=True)
    intro_poster = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Intro-Poster",
    )
    tap_to_play_label = models.CharField("Tap-to-play-Label", max_length=120, blank=True)
    accessible_video_label = models.CharField("Barrierefreie Video-Beschreibung", max_length=240, blank=True)
    scroll_video = models.ForeignKey(
        "wagtaildocs.Document", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Scroll-Hero-Video",
    )
    scroll_poster = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="Scroll-Hero-Poster",
    )
    hero_chapters = StreamField([("chapter", HeroChapterBlock())], blank=True, use_json_field=True)
    employer_cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)
    candidate_cta = StreamField([("cta", LinkBlock())], blank=True, max_num=1, use_json_field=True)
    follow_on_sections = StreamField([("section", RichSectionBlock())], blank=True, use_json_field=True)

    content_panels = [
            MultiFieldPanel([
            FieldPanel("intro_video"), FieldPanel("intro_video_url"), FieldPanel("intro_poster"), FieldPanel("tap_to_play_label"),
            FieldPanel("accessible_video_label"), FieldPanel("scroll_video"), FieldPanel("scroll_poster"),
        ], heading="Intro und Scroll-Hero"),
        FieldPanel("hero_chapters"),
        MultiFieldPanel([FieldPanel("employer_cta"), FieldPanel("candidate_cta")], heading="Zielgruppen-CTAs"),
        FieldPanel("follow_on_sections"),
    ]

    class Meta:
        verbose_name = "Startseite"
