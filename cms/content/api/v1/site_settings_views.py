from django.http import JsonResponse

from content.site_settings import KPSettings

from .site_settings import serialize_site_settings


def site_settings(request):
    settings = KPSettings.for_request(request)
    if settings is None:
        return JsonResponse({"error": "site settings not configured"}, status=404)
    return JsonResponse({"data": serialize_site_settings(settings)}, status=200)
