from urllib.parse import urlencode

from django.conf import settings
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem

from .api.v1.preview import create_preview_token


class AstroPreviewMenuItem(ActionMenuItem):
    label = "Astro-Vorschau"
    name = "astro-preview"
    icon_name = "view"
    order = 10

    def is_shown(self, context):
        return context.get("view") == "edit" and context.get("page") is not None and super().is_shown(context)

    def get_url(self, parent_context):
        page = parent_context["page"]
        token = create_preview_token(page)
        return f"{settings.FRONTEND_BASE_URL.rstrip('/')}/preview/?{urlencode({'token': token})}"


@hooks.register("register_page_action_menu_item")
def register_astro_preview_menu_item():
    return AstroPreviewMenuItem(order=10)
