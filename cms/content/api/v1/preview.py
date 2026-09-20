from django.conf import settings
from django.core import signing
from django.http import JsonResponse
from wagtail.models import Page, Revision

from .serializers import serialize_page


PREVIEW_MAX_AGE_SECONDS = 300
PREVIEW_SALT = "kp-cms-preview-v1"


def _signer():
    secret = getattr(settings, "PREVIEW_SIGNING_SECRET", "")
    if not secret:
        raise RuntimeError("PREVIEW_SIGNING_SECRET is not configured")
    return signing.TimestampSigner(key=secret, salt=PREVIEW_SALT)


def create_preview_token(page, revision_id=None):
    if revision_id is None:
        revision = page.get_latest_revision()
        revision_id = revision.id if revision else None
    if not revision_id:
        raise ValueError("A preview token requires a page revision")
    return _signer().sign_object({"page_id": page.pk, "revision_id": revision_id})


def preview_revision(request, token):
    try:
        payload = _signer().unsign_object(token, max_age=PREVIEW_MAX_AGE_SECONDS)
        page = Page.objects.get(pk=payload["page_id"])
        revision = Revision.objects.get(pk=payload["revision_id"], content_type=page.content_type)
        draft = revision.as_object()
    except (KeyError, TypeError, ValueError, signing.BadSignature, signing.SignatureExpired,
            Page.DoesNotExist, Revision.DoesNotExist, RuntimeError):
        return JsonResponse({"error": "preview token is invalid or expired"}, status=404)

    response = JsonResponse({"data": serialize_page(draft)})
    response["Cache-Control"] = "no-store"
    response["X-Robots-Tag"] = "noindex"
    return response
