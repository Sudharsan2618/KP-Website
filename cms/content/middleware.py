import logging

from django.conf import settings
from django.db import OperationalError
from django.http import JsonResponse


logger = logging.getLogger("kp.api")


class ApiFailureMiddleware:
    """Return a safe API 503 for transient CMS/database failures in production."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except (OperationalError, TimeoutError) as exc:
            if settings.DEBUG or not request.path.startswith("/api/v1/"):
                raise
            logger.error(
                "api_failure",
                extra={"path": request.path, "method": request.method, "error_type": type(exc).__name__},
            )
            return JsonResponse({"error": "cms_unavailable"}, status=503)
