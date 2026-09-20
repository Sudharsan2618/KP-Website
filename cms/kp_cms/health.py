from django.db import connection
from django.http import JsonResponse


def healthz(request):
    """Process liveness probe; it intentionally does not require the database."""
    return JsonResponse({"status": "ok"})


def readyz(request):
    """Readiness probe that verifies the configured PostgreSQL connection."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "not_ready"}, status=503)
    return JsonResponse({"status": "ready"})
