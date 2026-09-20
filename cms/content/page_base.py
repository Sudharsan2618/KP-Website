from wagtail.models import Page

from .seo import SEOFieldsMixin


class KPPageBase(SEOFieldsMixin, Page):
    """Shared base for public KP pages; content models add their own panels."""

    class Meta:
        abstract = True
