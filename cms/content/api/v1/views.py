from django.http import JsonResponse
from wagtail.models import Page

from .serializers import serialize_page


def page_by_path(request):
    path = request.GET.get("path", "").strip()
    if not path or not path.startswith("/") or not path.endswith("/") or "?" in path or "#" in path:
        return JsonResponse({"error": "path must be an absolute site path ending with /"}, status=400)

    page = Page.objects.live().filter(url_path=path).select_related("content_type").first()
    if page is None:
        return JsonResponse({"error": "published page not found"}, status=404)

    return JsonResponse({"data": serialize_page(page.specific)}, status=200)
