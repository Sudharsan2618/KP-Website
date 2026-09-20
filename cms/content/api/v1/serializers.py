from collections.abc import Mapping
from datetime import date, datetime
from types import SimpleNamespace

from rest_framework import serializers
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Page


COMMON_FIELD_NAMES = {
    "id", "path", "depth", "numchild", "title", "slug", "live", "has_unpublished_changes",
    "first_published_at", "last_published_at", "latest_revision_created_at", "seo_title",
    "search_description", "owner", "content_type", "translation_key", "locale", "alias_of",
    "live_revision", "latest_revision", "page_ptr",
}


def serialize_value(value):
    """Convert Wagtail/Django values into JSON-safe public API data."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        result = {str(key): serialize_value(item) for key, item in value.items()}
        if isinstance(value.get("page"), int):
            target = Page.objects.filter(pk=value["page"]).first()
            result["page"] = {"id": target.pk, "title": target.title, "url_path": target.url_path} if target else None
        for key, model_name in (("service", "Service"), ("testimonial", "Testimonial"), ("team_member", "TeamMember")):
            if isinstance(value.get(key), int):
                from content import snippets
                target = getattr(snippets, model_name).objects.filter(pk=value[key]).first()
                if target:
                    result[key] = {field.name: serialize_value(getattr(target, field.name)) for field in target._meta.fields if field.name not in {"id", "portrait"}}
                    if model_name == "TeamMember" and target.portrait_id:
                        result[key]["portrait"] = serialize_value(target.portrait)
        return result
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    if isinstance(value, StreamValue):
        return [serialize_value(dict(item)) for item in value.raw_data]
    if hasattr(value, "stream_data"):
        return serialize_value(value.stream_data)
    if hasattr(value, "block_type") and hasattr(value, "value"):
        return {"type": value.block_type, "value": serialize_value(value.value)}
    if hasattr(value, "url_path"):
        return {"id": value.pk, "title": value.title, "url_path": value.url_path}
    if hasattr(value, "file") and hasattr(value, "title"):
        file_url = getattr(value.file, "url", None) if value.file else None
        return {"id": value.pk, "title": value.title, "url": file_url}
    return str(value)


def serialize_seo(page):
    return {
        "title": getattr(page, "seo_title", "") or getattr(page, "title", ""),
        "description": getattr(page, "search_description", ""),
        "og_title": getattr(page, "og_title", ""),
        "og_description": getattr(page, "og_description", ""),
        "og_image": serialize_value(getattr(page, "og_image", None)),
        "canonical_url": getattr(page, "canonical_url", "") or None,
        "noindex": bool(getattr(page, "noindex", False)),
        "navigation_label": getattr(page, "navigation_label", "") or getattr(page, "title", ""),
        "last_reviewed": serialize_value(getattr(page, "last_reviewed", None)),
    }


def serialize_page_fields(page):
    data = {}
    for field in page._meta.concrete_fields:
        name = field.name
        if name in COMMON_FIELD_NAMES or name.endswith("_ptr"):
            continue
        value = getattr(page, name, None)
        data[name] = serialize_value(value)
    return data


def serialize_page(page):
    """Return the stable v1 page envelope; publication filtering belongs to views."""
    updated = getattr(page, "latest_revision_created_at", None) or getattr(page, "last_published_at", None)
    return {
        "type": f"{page._meta.app_label}.{page.__class__.__name__}",
        "id": page.pk,
        "title": page.title,
        "slug": page.slug,
        "url_path": page.url_path,
        "seo": serialize_seo(page),
        "updated_at": serialize_value(updated),
        "fields": serialize_page_fields(page),
    }


class PageSerializer(serializers.Serializer):
    """Version 1 serializer used by all published page endpoints."""

    def to_representation(self, instance):
        return serialize_page(instance)
